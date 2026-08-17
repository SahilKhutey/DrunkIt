"""Payment attempt model."""

from __future__ import annotations

from decimal import Decimal
from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import PaymentAttemptStatus


class PaymentAttempt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Payment attempt tracking model for individual payment attempts."""

    __tablename__ = "payment_attempts"

    payment_id: Mapped[str] = mapped_column(String(36), ForeignKey("payments.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[PaymentAttemptStatus] = mapped_column(
        Enum(PaymentAttemptStatus, name="payment_attempt_status"),
        nullable=False,
        default=PaymentAttemptStatus.CREATED,
    )
    provider_attempt_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
