"""Endpoint de consulta del registro de auditoria."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import audit_log as crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit", tags=["auditoria"])


@router.get("/logs", response_model=list[AuditLogRead])
def list_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AuditLogRead]:
    """Devuelve los eventos de auditoria mas recientes."""
    return crud.list_logs(db, limit=limit)
