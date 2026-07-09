"""Endpoints de certificados digitales emitidos por la CA simulada.

Emitir, consultar, validar (confianza + vigencia) y revocar. Requieren autenticacion.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import certificate as crud
from app.crypto.ca import issue_certificate, validate_certificate
from app.db.session import get_db
from app.models.user import User
from app.schemas.certificate import (
    CertificateIssued,
    CertificateRead,
    CertificateValidation,
)

router = APIRouter(prefix="/certificates", tags=["certificados"])


@router.post("", response_model=CertificateIssued, status_code=status.HTTP_201_CREATED)
def emit_certificate(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificateIssued:
    """Emite un certificado X.509 firmado por la CA para el usuario autenticado."""
    private_pem, public_pem, cert_pem, serial, expires_at = issue_certificate(
        common_name=current_user.username
    )
    cert = crud.create_certificate(
        db, current_user.id, serial, public_pem, cert_pem, expires_at
    )
    return CertificateIssued(
        id=cert.id,
        user_id=cert.user_id,
        serial=cert.serial,
        status=cert.status,
        issued_at=cert.issued_at,
        expires_at=cert.expires_at,
        cert_pem=cert_pem,
        private_key_pem=private_pem,
    )


@router.get("", response_model=list[CertificateRead])
def list_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CertificateRead]:
    return crud.list_certificates(db, user_id=current_user.id)


@router.get("/{cert_id}", response_model=CertificateRead)
def get_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificateRead:
    cert = crud.get_certificate(db, cert_id)
    if cert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificado no encontrado")
    return cert


@router.get("/{cert_id}/validate", response_model=CertificateValidation)
def validate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificateValidation:
    """Valida confianza (firma de la CA) y vigencia; respeta el estado revocado en BD."""
    cert = crud.get_certificate(db, cert_id)
    if cert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificado no encontrado")

    if cert.status == "revoked":
        return CertificateValidation(
            certificate_id=cert.id,
            db_status=cert.status,
            valid=False,
            detail="El certificado fue revocado",
        )

    valido, detalle = validate_certificate(cert.cert_pem)
    # Refleja la expiracion detectada en el estado almacenado.
    if not valido and "expirado" in detalle and cert.status != "expired":
        crud.set_status(db, cert, "expired")

    return CertificateValidation(
        certificate_id=cert.id,
        db_status=cert.status,
        valid=valido,
        detail=detalle,
    )


@router.post("/{cert_id}/revoke", response_model=CertificateRead)
def revoke_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificateRead:
    cert = crud.get_certificate(db, cert_id)
    if cert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Certificado no encontrado")
    return crud.set_status(db, cert, "revoked")
