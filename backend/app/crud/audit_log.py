"""Operaciones sobre el registro de auditoria."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_log(
    db: Session,
    event_type: str,
    detail: str | None = None,
    user_id: int | None = None,
    ip: str | None = None,
) -> AuditLog:
    log = AuditLog(user_id=user_id, event_type=event_type, detail=detail, ip=ip)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_logs(db: Session, limit: int = 100) -> list[AuditLog]:
    stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    return list(db.scalars(stmt))
