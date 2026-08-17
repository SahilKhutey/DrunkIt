"""Payment database model."""

from __future__ import annotations

from decimal import Decimal
from sqlalchemy import Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import PaymentMethodType, PaymentStatus


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Payment aggregate root model."""

    __tablename__ = "payments"

    order_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        nullable=False,
        default=PaymentStatus.CREATED,
    )
    method: Mapped[PaymentMethodType] = mapped_column(
        Enum(PaymentMethodType, name="payment_method"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
