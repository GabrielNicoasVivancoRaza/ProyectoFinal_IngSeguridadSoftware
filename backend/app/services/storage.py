"""Almacenamiento en disco de los archivos subidos."""
import os
import uuid
from pathlib import Path

from app.core.config import settings


def save_upload(content: bytes, filename: str) -> str:
    """Guarda el contenido con un nombre unico y devuelve la ruta de almacenamiento."""
    storage = Path(settings.storage_dir)
    storage.mkdir(parents=True, exist_ok=True)
    # os.path.basename evita path traversal a partir del nombre original.
    safe_name = os.path.basename(filename) or "archivo"
    stored_name = f"{uuid.uuid4().hex}_{safe_name}"
    path = storage / stored_name
    path.write_bytes(content)
    return str(path)
