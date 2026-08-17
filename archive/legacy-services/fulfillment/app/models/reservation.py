"""Inventory reservation model."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class InventoryReservation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Inventory reservation model with TTL expiration."""

    __tablename__ = "inventory_reservations"

    order_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    warehouse_id: Mapped[str] = mapped_column(String(36), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="reserved")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
