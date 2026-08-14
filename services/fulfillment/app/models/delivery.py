"""Delivery database model."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import DeliveryStatus


class Delivery(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Last-mile delivery tracking aggregate model."""

    __tablename__ = "deliveries"

    order_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    fulfillment_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    courier_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="delivery_status"),
        nullable=False,
        default=DeliveryStatus.CREATED,
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
