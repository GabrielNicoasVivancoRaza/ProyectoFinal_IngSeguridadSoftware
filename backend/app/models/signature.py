"""Modelo de firma digital aplicada a un documento."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Signature(Base):
    __tablename__ = "signatures"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    cert_id: Mapped[int | None] = mapped_column(ForeignKey("certificates.id"), nullable=True)
    signature_b64: Mapped[str] = mapped_column(Text)
    algorithm: Mapped[str] = mapped_column(String(50), default="RSA-PSS-SHA256")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    document: Mapped["Document"] = relationship(back_populates="signatures")  # noqa: F821
