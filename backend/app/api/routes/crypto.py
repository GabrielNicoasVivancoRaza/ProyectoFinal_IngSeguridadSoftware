"""Endpoints de cifrado y descifrado de archivos con AES-256-GCM.

Requieren autenticacion. Trabajan sobre el archivo subido y devuelven el
resultado como descarga binaria (no se persiste en el servidor).
"""
from cryptography.exceptions import InvalidTag
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.api.deps import get_current_user
from app.crypto.symmetric import decrypt_bytes, encrypt_bytes
from app.models.user import User

router = APIRouter(prefix="/crypto", tags=["cifrado"])


def _descarga(content: bytes, filename: str) -> Response:
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/encrypt")
async def encrypt_file(
    file: UploadFile = File(...),
    password: str = Form(..., min_length=8),
    current_user: User = Depends(get_current_user),
) -> Response:
    data = await file.read()
    blob = encrypt_bytes(data, password)
    return _descarga(blob, f"{file.filename or 'archivo'}.enc")


@router.post("/decrypt")
async def decrypt_file(
    file: UploadFile = File(...),
    password: str = Form(..., min_length=8),
    current_user: User = Depends(get_current_user),
) -> Response:
    blob = await file.read()
    try:
        data = decrypt_bytes(blob, password)
    except (InvalidTag, ValueError) as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Contrasena incorrecta o archivo cifrado invalido/alterado",
        ) from exc
    nombre = (file.filename or "archivo").removesuffix(".enc") or "archivo"
    return _descarga(data, nombre)
