"""Modelo de certificado digital emitido por la CA simulada."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    serial: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    public_key: Mapped[str] = mapped_column(Text)
    cert_pem: Mapped[str] = mapped_column(Text)
    # Estados posibles: valid | revoked | expired
    status: Mapped[str] = mapped_column(String(20), default="valid")
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="certificates")  # noqa: F821
