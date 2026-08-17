"""Order aggregate database model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Enum, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import FulfillmentStatus, OrderStatus, PaymentStatus


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Order aggregate root entity model."""

    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("consumer_id", "idempotency_key", name="uq_consumer_idempotency"),
    )

    order_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.DRAFT,
        nullable=False,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    fulfillment_status: Mapped[FulfillmentStatus] = mapped_column(
        Enum(FulfillmentStatus, name="fulfillment_status"),
        default=FulfillmentStatus.NOT_STARTED,
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    tax: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    compliance_decision_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    compliance_policy_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
