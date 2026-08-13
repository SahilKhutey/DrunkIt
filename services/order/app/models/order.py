import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    RESERVING = "RESERVING"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAYMENT_AUTHORIZED = "PAYMENT_AUTHORIZED"
    CONFIRMED = "CONFIRMED"
    FULFILMENT = "FULFILMENT"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    FAILED = "FAILED"


class Order(Base):

    __tablename__ = "orders_d9"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )

    subtotal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    delivery_fee: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    taxes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    discount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="INR",
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
