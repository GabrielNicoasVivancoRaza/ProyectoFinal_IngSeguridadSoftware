"""Schema Pydantic para el registro de auditoria."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: int
    user_id: int | None
    event_type: str
    detail: str | None
    ip: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
