"""Endpoints de cifrado y descifrado de archivos con AES-256-GCM.

Requieren autenticacion. Trabajan sobre el archivo subido y devuelven el
resultado como descarga binaria (no se persiste en el servidor).
"""
from cryptography.exceptions import InvalidTag
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.api.deps import get_current_user
from app.crypto.asymmetric import generate_keypair, sign, verify
from app.crypto.symmetric import decrypt_bytes, encrypt_bytes
from app.models.user import User
from app.schemas.crypto import KeyPair, SignatureResult, VerifyResult

router = APIRouter(prefix="/crypto", tags=["cifrado y firma"])


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


@router.post("/keys/generate", response_model=KeyPair)
def generate_keys(current_user: User = Depends(get_current_user)) -> KeyPair:
    """Genera un par de claves RSA-2048. La clave privada solo se muestra aqui."""
    private_pem, public_pem = generate_keypair()
    return KeyPair(private_key_pem=private_pem, public_key_pem=public_pem)


@router.post("/sign", response_model=SignatureResult)
async def sign_document(
    file: UploadFile = File(...),
    private_key_pem: str = Form(...),
    current_user: User = Depends(get_current_user),
) -> SignatureResult:
    """Firma digitalmente un archivo con la clave privada RSA (RSA-PSS + SHA-256)."""
    data = await file.read()
    try:
        signature_b64 = sign(data, private_key_pem)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Clave privada invalida"
        ) from exc
    return SignatureResult(signature_b64=signature_b64)


@router.post("/verify", response_model=VerifyResult)
async def verify_signature(
    file: UploadFile = File(...),
    public_key_pem: str = Form(...),
    signature_b64: str = Form(...),
    current_user: User = Depends(get_current_user),
) -> VerifyResult:
    """Verifica la firma de un archivo. Si el documento fue alterado, la firma es invalida."""
    data = await file.read()
    try:
        valido = verify(data, signature_b64, public_key_pem)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Clave publica o firma con formato invalido"
        ) from exc
    return VerifyResult(
        valid=valido,
        detail="Firma valida" if valido else "Firma invalida o documento alterado",
    )
