"""Funciones de hash SHA-256 para verificar la integridad de documentos."""
import hashlib


def sha256_bytes(data: bytes) -> str:
    """Devuelve el hash SHA-256 (hex) de una secuencia de bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    """Devuelve el hash SHA-256 (hex) del contenido de un archivo, leyendo por bloques."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()
