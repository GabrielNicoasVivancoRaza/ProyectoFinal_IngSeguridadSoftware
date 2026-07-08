"""Utilidades de seguridad: hashing y verificacion de contrasenas con bcrypt."""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Devuelve el hash bcrypt de una contrasena en texto plano."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Comprueba si una contrasena en texto plano coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)
