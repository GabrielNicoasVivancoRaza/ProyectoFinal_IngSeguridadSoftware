"""Servicio de auditoria: registra eventos del sistema de forma uniforme."""
from fastapi import Request
from sqlalchemy.orm import Session

from app.crud import audit_log as crud


def record(
    db: Session,
    event_type: str,
    detail: str | None = None,
    user_id: int | None = None,
    request: Request | None = None,
) -> None:
    """Registra un evento de auditoria, capturando la IP de la peticion si esta disponible."""
    ip = request.client.host if request and request.client else None
    crud.create_log(db, event_type=event_type, detail=detail, user_id=user_id, ip=ip)
