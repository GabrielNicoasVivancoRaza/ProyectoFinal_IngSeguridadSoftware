"""Operaciones CRUD sobre la entidad Documento."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


def get_document(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)


def list_documents(db: Session, include_deleted: bool = False) -> list[Document]:
    stmt = select(Document)
    if not include_deleted:
        stmt = stmt.where(Document.is_deleted.is_(False))
    return list(db.scalars(stmt.order_by(Document.id)))


def create_document(
    db: Session, user_id: int, filename: str, storage_path: str, sha256: str
) -> Document:
    doc = Document(
        user_id=user_id,
        filename=filename,
        storage_path=storage_path,
        sha256=sha256,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def soft_delete_document(db: Session, doc: Document) -> None:
    """Eliminacion logica: el documento se marca como borrado, no se elimina fisicamente."""
    doc.is_deleted = True
    db.commit()
