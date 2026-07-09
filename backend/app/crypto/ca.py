"""Autoridad Certificadora (CA) simulada.

Genera y persiste una CA raiz (clave + certificado autofirmado), emite
certificados X.509 para usuarios y valida su confianza (firma de la CA + vigencia).
"""
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from app.core.config import settings

_CA_KEY_FILE = "ca_key.pem"
_CA_CERT_FILE = "ca_cert.pem"


def _build_ca() -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "EC"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CA Simulada - Proyecto Seguridad"),
            x509.NameAttribute(NameOID.COMMON_NAME, "CA Raiz Simulada"),
        ]
    )
    now = datetime.now(UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    return key, cert


def ensure_ca() -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    """Carga la CA raiz desde disco; si no existe, la crea y la persiste."""
    ca_dir = Path(settings.ca_dir)
    ca_dir.mkdir(parents=True, exist_ok=True)
    key_path = ca_dir / _CA_KEY_FILE
    cert_path = ca_dir / _CA_CERT_FILE

    if key_path.exists() and cert_path.exists():
        key = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
        cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
        return key, cert

    key, cert = _build_ca()
    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return key, cert


def issue_certificate(
    common_name: str, validity_days: int = 365
) -> tuple[str, str, str, str, datetime]:
    """Emite un certificado X.509 firmado por la CA para un nuevo par de claves.

    Devuelve (private_key_pem, public_key_pem, cert_pem, serial_hex, expires_at).
    validity_days negativo produce un certificado ya expirado (util para pruebas).
    """
    ca_key, ca_cert = ensure_ca()
    subject_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    now = datetime.now(UTC)
    not_after = now + timedelta(days=validity_days)
    not_before = min(now - timedelta(minutes=1), not_after - timedelta(minutes=1))
    serial = x509.random_serial_number()

    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)]))
        .issuer_name(ca_cert.subject)
        .public_key(subject_key.public_key())
        .serial_number(serial)
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    private_pem = subject_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = subject_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    return private_pem, public_pem, cert_pem, f"{serial:x}", not_after


def validate_certificate(cert_pem: str) -> tuple[bool, str]:
    """Valida confianza y vigencia de un certificado.

    Comprueba: (1) esta firmado por la CA, (2) no fue alterado, (3) esta vigente.
    """
    _, ca_cert = ensure_ca()
    try:
        cert = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))
    except ValueError:
        return False, "Certificado ilegible o alterado"

    # 1. Verificar que la CA lo firmo (cadena de confianza).
    try:
        ca_cert.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
    except InvalidSignature:
        return False, "El certificado no fue emitido por la CA (no confiable)"

    # 2. Verificar vigencia.
    now = datetime.now(UTC)
    if now < cert.not_valid_before_utc:
        return False, "El certificado aun no es valido"
    if now > cert.not_valid_after_utc:
        return False, "El certificado esta expirado"

    return True, "Certificado valido y confiable"
