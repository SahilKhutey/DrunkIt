"""Identity Verification Request Models."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class VerificationRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "verification_requests"

    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)  # AADHAAR|PASSPORT|DRIVING_LICENSE
    document_number_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    document_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)  # PENDING|SUCCESS|FAILED
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
