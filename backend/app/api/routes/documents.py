"""Endpoints CRUD de documentos, con hash SHA-256 y verificacion de integridad.

Todos los endpoints requieren autenticacion (JWT).
"""
import os

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import document as crud
from app.crypto.hashing import sha256_bytes, sha256_file
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentRead, IntegrityCheck
from app.services.audit import record
from app.services.storage import save_upload

router = APIRouter(prefix="/documents", tags=["documentos"])


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    content = await file.read()
    sha256 = sha256_bytes(content)
    filename = file.filename or "archivo"
    storage_path = save_upload(content, filename)
    doc = crud.create_document(db, current_user.id, filename, storage_path, sha256)
    record(db, "document_upload", detail=filename, user_id=current_user.id, request=request)
    return doc


@router.get("", response_model=list[DocumentRead])
def list_documents(
    include_deleted: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentRead]:
    return crud.list_documents(db, include_deleted=include_deleted)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    doc = crud.get_document(db, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
    return doc


@router.get("/{document_id}/verify", response_model=IntegrityCheck)
def verify_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntegrityCheck:
    """Recalcula el hash del archivo almacenado y lo compara con el guardado."""
    doc = crud.get_document(db, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")

    if not os.path.exists(doc.storage_path):
        return IntegrityCheck(
            document_id=doc.id,
            stored_sha256=doc.sha256,
            actual_sha256=None,
            valid=False,
            detail="El archivo no se encuentra en el almacenamiento",
        )

    actual = sha256_file(doc.storage_path)
    valid = actual == doc.sha256
    record(
        db,
        "document_verify",
        detail=f"doc={doc.id} valid={valid}",
        user_id=current_user.id,
        request=request,
    )
    return IntegrityCheck(
        document_id=doc.id,
        stored_sha256=doc.sha256,
        actual_sha256=actual,
        valid=valid,
        detail="Integridad verificada" if valid else "El documento fue alterado",
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    doc = crud.get_document(db, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
    crud.soft_delete_document(db, doc)
