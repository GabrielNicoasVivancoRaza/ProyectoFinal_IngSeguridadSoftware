"""Endpoints CRUD de documentos, con hash SHA-256 y verificacion de integridad."""
import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.crud import document as crud
from app.crud import user as crud_user
from app.crypto.hashing import sha256_bytes, sha256_file
from app.db.session import get_db
from app.schemas.document import DocumentRead, IntegrityCheck
from app.services.storage import save_upload

router = APIRouter(prefix="/documents", tags=["documentos"])


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentRead:
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    content = await file.read()
    sha256 = sha256_bytes(content)
    storage_path = save_upload(content, file.filename or "archivo")
    return crud.create_document(db, user_id, file.filename or "archivo", storage_path, sha256)


@router.get("", response_model=list[DocumentRead])
def list_documents(
    include_deleted: bool = False, db: Session = Depends(get_db)
) -> list[DocumentRead]:
    return crud.list_documents(db, include_deleted=include_deleted)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)) -> DocumentRead:
    doc = crud.get_document(db, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
    return doc


@router.get("/{document_id}/verify", response_model=IntegrityCheck)
def verify_document(document_id: int, db: Session = Depends(get_db)) -> IntegrityCheck:
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
    return IntegrityCheck(
        document_id=doc.id,
        stored_sha256=doc.sha256,
        actual_sha256=actual,
        valid=valid,
        detail="Integridad verificada" if valid else "El documento fue alterado",
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    doc = crud.get_document(db, document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado")
    crud.soft_delete_document(db, doc)
