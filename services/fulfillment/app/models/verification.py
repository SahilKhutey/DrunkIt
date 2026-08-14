"""Delivery verification database model."""

from __future__ import annotations

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import VerificationStatus


class DeliveryVerification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Customer age/identity verification model for regulated alcohol delivery handoff."""

    __tablename__ = "delivery_verifications"

    delivery_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        nullable=False,
        default=VerificationStatus.NOT_STARTED,
    )
    verification_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
