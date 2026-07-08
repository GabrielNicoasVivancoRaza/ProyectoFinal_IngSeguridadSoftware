"""Schemas Pydantic para documentos."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: int
    user_id: int
    filename: str
    sha256: str
    is_deleted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntegrityCheck(BaseModel):
    """Resultado de verificar la integridad de un documento por su hash."""

    document_id: int
    stored_sha256: str
    actual_sha256: str | None
    valid: bool
    detail: str
