"""Consumer service database models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class ConsumerProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Consumer profile vault holding identity and level status."""

    __tablename__ = "consumer_profiles"

    user_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)

    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)

    consumer_level: Mapped[str] = mapped_column(
        String(32), default="C1_REGISTERED", nullable=False, index=True
    )  # C0_ANONYMOUS | C1_REGISTERED | C2_AGE_VERIFIED | C3_FULL_KYC
    is_age_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    age_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    kyc_status: Mapped[str] = mapped_column(String(32), default="NOT_STARTED", nullable=False)
    primary_jurisdiction: Mapped[str] = mapped_column(String(64), default="IN-KA", nullable=False, index=True)

    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    trust_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    addresses: Mapped[list["DeliveryAddress"]] = relationship(
        "DeliveryAddress", back_populates="consumer", cascade="all, delete-orphan"
    )
    verifications: Mapped[list["AgeVerificationRecord"]] = relationship(
        "AgeVerificationRecord", back_populates="consumer", cascade="all, delete-orphan"
    )


class DeliveryAddress(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Consumer delivery address book."""

    __tablename__ = "delivery_addresses"

    consumer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("consumer_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    label: Mapped[str] = mapped_column(String(32), default="Home", nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(128), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(32), nullable=False)

    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    landmark: Mapped[str | None] = mapped_column(String(128), nullable=True)

    city: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    pincode: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    jurisdiction: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivery_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    consumer: Mapped["ConsumerProfile"] = relationship("ConsumerProfile", back_populates="addresses")


class AgeVerificationRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Audit trail of age verification checks."""

    __tablename__ = "age_verification_records"

    consumer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("consumer_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    verification_type: Mapped[str] = mapped_column(String(32), nullable=False)  # AADHAAR_OKYC | PAN_V2 | DL_API | MANUAL_DOC
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)
    document_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    verified_age: Mapped[int] = mapped_column(Integer, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # PASSED | FAILED | REJECTED
    verifier_provider: Mapped[str] = mapped_column(String(64), nullable=False)

    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    consumer: Mapped["ConsumerProfile"] = relationship("ConsumerProfile", back_populates="verifications")


class ConsumerPreferences(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Consumer notification & category preferences."""

    __tablename__ = "consumer_preferences"

    consumer_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)

    favorite_categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    allow_promotions: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferred_payment_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
