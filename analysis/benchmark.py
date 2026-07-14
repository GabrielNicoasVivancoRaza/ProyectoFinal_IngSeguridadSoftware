"""Mide el rendimiento de las operaciones criptograficas de la plataforma.

Ejecuta experimentos repetidos sobre los modulos reales del backend y exporta:
  - results/timings.csv : cada medicion individual (ms)
  - results/rates.csv   : tasas de deteccion de alteraciones y de autenticacion

Uso:  python benchmark.py
"""
import csv
import os
import secrets
import sys
import tempfile
import time
from pathlib import Path

# Permite importar los modulos del backend.
BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.config import settings  # noqa: E402

# La CA de pruebas se genera en un directorio temporal (no toca la del servidor).
settings.ca_dir = tempfile.mkdtemp(prefix="bench_ca_")

from app.core.security import hash_password, verify_password  # noqa: E402
from app.crypto.asymmetric import generate_keypair, sign, verify  # noqa: E402
from app.crypto.ca import issue_certificate, validate_certificate  # noqa: E402
from app.crypto.hashing import sha256_bytes  # noqa: E402
from app.crypto.symmetric import decrypt_bytes, encrypt_bytes  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "results"
RESULTS.mkdir(exist_ok=True)

SIZES = {"10 KB": 10 * 1024, "100 KB": 100 * 1024, "1 MB": 1024 * 1024}
PASSWORD = "claveDePrueba123"

timings: list[dict] = []


def medir(operacion: str, size_label: str, size_bytes: int, run: int, fn, *args):
    """Ejecuta fn midiendo su duracion en milisegundos y registra el resultado."""
    inicio = time.perf_counter()
    resultado = fn(*args)
    duracion_ms = (time.perf_counter() - inicio) * 1000
    timings.append(
        {
            "operation": operacion,
            "size_label": size_label,
            "size_bytes": size_bytes,
            "run": run,
            "duration_ms": round(duracion_ms, 4),
        }
    )
    return resultado


def benchmark_por_tamano():
    """Hash, cifrado/descifrado AES y firma/verificacion RSA para distintos tamanos."""
    priv, pub = generate_keypair()

    for etiqueta, tam in SIZES.items():
        datos = secrets.token_bytes(tam)
        print(f"  midiendo tamano {etiqueta}...")

        for i in range(30):
            medir("Hash SHA-256", etiqueta, tam, i, sha256_bytes, datos)

        for i in range(10):
            blob = medir("Cifrado AES-256-GCM", etiqueta, tam, i, encrypt_bytes, datos, PASSWORD)
            medir("Descifrado AES-256-GCM", etiqueta, tam, i, decrypt_bytes, blob, PASSWORD)

        for i in range(10):
            firma = medir("Firma RSA-PSS", etiqueta, tam, i, sign, datos, priv)
            medir("Verificacion de firma", etiqueta, tam, i, verify, datos, firma, pub)


def benchmark_operaciones_fijas():
    """Operaciones cuyo coste no depende del tamano del archivo."""
    print("  midiendo generacion de claves y certificados...")

    for i in range(5):
        medir("Generacion de claves RSA-2048", "n/a", 0, i, generate_keypair)

    certs = []
    for i in range(5):
        _, _, cert_pem, _, _ = medir("Emision de certificado", "n/a", 0, i, issue_certificate, f"user{i}")
        certs.append(cert_pem)

    for i in range(20):
        medir("Validacion de certificado", "n/a", 0, i, validate_certificate, certs[i % len(certs)])

    print("  midiendo hashing de contrasenas (bcrypt)...")
    for i in range(10):
        h = medir("Hash de contrasena (bcrypt)", "n/a", 0, i, hash_password, PASSWORD)
        medir("Verificacion de contrasena", "n/a", 0, i, verify_password, PASSWORD, h)


def tasa_deteccion_alteraciones(intentos: int = 50) -> dict:
    """Altera documentos y comprueba que los 3 mecanismos detectan la manipulacion."""
    print(f"  probando deteccion de alteraciones ({intentos} intentos)...")
    priv, pub = generate_keypair()
    detectados_hash = detectados_firma = detectados_aes = 0

    for _ in range(intentos):
        original = secrets.token_bytes(2048)
        alterado = bytearray(original)
        pos = secrets.randbelow(len(alterado))
        alterado[pos] ^= 0xFF  # cambia un byte
        alterado = bytes(alterado)

        # 1. Integridad por hash
        if sha256_bytes(original) != sha256_bytes(alterado):
            detectados_hash += 1

        # 2. Firma digital sobre el documento alterado
        firma = sign(original, priv)
        if not verify(alterado, firma, pub):
            detectados_firma += 1

        # 3. Cifrado autenticado AES-GCM (tag invalido)
        blob = bytearray(encrypt_bytes(original, PASSWORD))
        blob[-1] ^= 0x01
        try:
            decrypt_bytes(bytes(blob), PASSWORD)
        except Exception:
            detectados_aes += 1

    return {
        "Deteccion por hash SHA-256": (detectados_hash, intentos),
        "Deteccion por firma digital": (detectados_firma, intentos),
        "Deteccion por AES-GCM (tag)": (detectados_aes, intentos),
    }


def tasa_autenticacion(intentos: int = 15) -> dict:
    """Mide exito con credenciales correctas y rechazo con credenciales incorrectas."""
    print(f"  probando autenticacion ({intentos * 2} intentos)...")
    hashed = hash_password(PASSWORD)

    exitos = sum(verify_password(PASSWORD, hashed) for _ in range(intentos))
    rechazos = sum(
        not verify_password(f"claveIncorrecta{i}", hashed) for i in range(intentos)
    )
    return {
        "Autenticacion exitosa (clave correcta)": (exitos, intentos),
        "Rechazo correcto (clave incorrecta)": (rechazos, intentos),
    }


def main():
    print("Ejecutando benchmark criptografico...")
    inicio = time.perf_counter()

    benchmark_por_tamano()
    benchmark_operaciones_fijas()

    tasas = {}
    tasas.update(tasa_deteccion_alteraciones())
    tasas.update(tasa_autenticacion())

    # --- Exportar mediciones de tiempo ---
    ruta_timings = RESULTS / "timings.csv"
    with open(ruta_timings, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["operation", "size_label", "size_bytes", "run", "duration_ms"]
        )
        writer.writeheader()
        writer.writerows(timings)

    # --- Exportar tasas ---
    ruta_rates = RESULTS / "rates.csv"
    with open(ruta_rates, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "successes", "total", "rate_pct"])
        for metrica, (ok, total) in tasas.items():
            writer.writerow([metrica, ok, total, round(100 * ok / total, 2)])

    duracion = time.perf_counter() - inicio
    print(f"\nListo en {duracion:.1f}s")
    print(f"  {len(timings)} mediciones -> {ruta_timings}")
    print(f"  {len(tasas)} tasas       -> {ruta_rates}")


if __name__ == "__main__":
    main()
