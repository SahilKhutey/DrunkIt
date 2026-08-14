"""Consumer verification status database model."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import VerificationMethod, VerificationStatus


class ConsumerVerification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Privacy-preserving consumer verification status model."""

    __tablename__ = "consumer_verifications"

    consumer_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.NOT_STARTED,
        nullable=False,
    )
    method: Mapped[VerificationMethod | None] = mapped_column(
        Enum(VerificationMethod, name="verification_method"),
        nullable=True,
    )
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
