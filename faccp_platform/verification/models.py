"""Verification Record database model enforcing PII privacy boundaries."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base


class VerificationRecord(Base):
    """Verification record storing state metadata without raw ID document PII."""

    __tablename__ = "verification_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    verification_type: Mapped[str] = mapped_column(String(100), default="age_and_identity")
    state: Mapped[str] = mapped_column(String(50), default="not_started")
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    policy_version: Mapped[str] = mapped_column(String(50), default="2026.08")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
