"""Criptografia asimetrica RSA: generacion de claves y firma digital.

- Claves RSA-2048.
- Firma digital con RSA-PSS + SHA-256 (detecta alteraciones del documento).
"""
import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

_PSS = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)


def generate_keypair(key_size: int = 2048) -> tuple[str, str]:
    """Genera un par RSA y devuelve (clave_privada_pem, clave_publica_pem)."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    return private_pem, public_pem


def sign(data: bytes, private_key_pem: str) -> str:
    """Firma los datos con la clave privada RSA (RSA-PSS + SHA-256). Devuelve base64."""
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"), password=None
    )
    signature = private_key.sign(data, _PSS, hashes.SHA256())
    return base64.b64encode(signature).decode("utf-8")


def verify(data: bytes, signature_b64: str, public_key_pem: str) -> bool:
    """Verifica una firma RSA-PSS. Devuelve True si es valida, False si no."""
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    try:
        public_key.verify(
            base64.b64decode(signature_b64), data, _PSS, hashes.SHA256()
        )
    except InvalidSignature:
        return False
    return True
