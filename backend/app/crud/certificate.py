"""Operaciones CRUD sobre certificados digitales."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.certificate import Certificate


def get_certificate(db: Session, cert_id: int) -> Certificate | None:
    return db.get(Certificate, cert_id)


def list_certificates(db: Session, user_id: int | None = None) -> list[Certificate]:
    stmt = select(Certificate)
    if user_id is not None:
        stmt = stmt.where(Certificate.user_id == user_id)
    return list(db.scalars(stmt.order_by(Certificate.id)))


def create_certificate(
    db: Session,
    user_id: int,
    serial: str,
    public_key: str,
    cert_pem: str,
    expires_at: datetime,
) -> Certificate:
    cert = Certificate(
        user_id=user_id,
        serial=serial,
        public_key=public_key,
        cert_pem=cert_pem,
        status="valid",
        expires_at=expires_at,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def set_status(db: Session, cert: Certificate, status: str) -> Certificate:
    cert.status = status
    db.commit()
    db.refresh(cert)
    return cert
