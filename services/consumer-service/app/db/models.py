"""Consumer Profile & Identity Vault Models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class ConsumerProfile(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "consumer_profiles"

    account_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    full_name_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    date_of_birth_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    date_of_birth_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    verification_level: Mapped[str] = mapped_column(
        String(32), default="C0_GUEST", nullable=False, index=True
    )
    age_eligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    state_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    default_delivery_address: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class ConsumerVerificationRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "consumer_verifications"

    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    verification_type: Mapped[str] = mapped_column(String(32), nullable=False)  # AADHAAR|PASSPORT|DRIVING_LICENSE
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # VERIFIED|FAILED|REJECTED
    confidence_score: Mapped[float] = mapped_column(default=1.0, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    document_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
