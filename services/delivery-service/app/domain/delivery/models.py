import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.delivery.enums import DeliveryStatus


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    order_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    retailer_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    store_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    consumer_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    driver_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    pickup_address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    dropoff_address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus),
        nullable=False,
        default=DeliveryStatus.REQUESTED,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
