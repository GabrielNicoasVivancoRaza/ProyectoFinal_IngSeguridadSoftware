"""Cifrado simetrico de archivos con AES-256-GCM.

La clave se deriva de una contrasena mediante PBKDF2-HMAC-SHA256. El formato del
blob cifrado es: salt(16) || nonce(12) || ciphertext+tag.
GCM es un modo autenticado: si la contrasena es incorrecta o el dato fue alterado,
el descifrado falla con InvalidTag.
"""
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_LEN = 16
NONCE_LEN = 12
KEY_LEN = 32  # AES-256
PBKDF2_ITERATIONS = 200_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Deriva una clave AES-256 a partir de una contrasena y un salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(data: bytes, password: str) -> bytes:
    """Cifra datos con AES-256-GCM. Devuelve salt || nonce || ciphertext+tag."""
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(password, salt)
    ciphertext = AESGCM(key).encrypt(nonce, data, None)
    return salt + nonce + ciphertext


def decrypt_bytes(blob: bytes, password: str) -> bytes:
    """Descifra un blob producido por encrypt_bytes.

    Lanza cryptography.exceptions.InvalidTag si la contrasena es incorrecta o el
    contenido fue alterado; ValueError si el blob es demasiado corto.
    """
    minimo = SALT_LEN + NONCE_LEN + 16  # 16 = tamano minimo del tag GCM
    if len(blob) < minimo:
        raise ValueError("Datos cifrados invalidos o incompletos")
    salt = blob[:SALT_LEN]
    nonce = blob[SALT_LEN : SALT_LEN + NONCE_LEN]
    ciphertext = blob[SALT_LEN + NONCE_LEN :]
    key = derive_key(password, salt)
    return AESGCM(key).decrypt(nonce, ciphertext, None)
