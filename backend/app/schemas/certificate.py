"""Schemas Pydantic para certificados digitales."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CertificateRead(BaseModel):
    id: int
    user_id: int
    serial: str
    status: str
    issued_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CertificateIssued(CertificateRead):
    """Respuesta al emitir: incluye el PEM del certificado y la clave privada.

    La clave privada se entrega una unica vez y NO se almacena en el servidor.
    """

    cert_pem: str
    private_key_pem: str


class CertificateValidation(BaseModel):
    certificate_id: int
    db_status: str
    valid: bool
    detail: str
