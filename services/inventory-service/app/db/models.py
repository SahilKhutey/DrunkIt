"""Inventory service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class InventoryItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Store SKU inventory tracking balance."""

    __tablename__ = "inventory_items"

    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sku_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    __table_args__ = (
        Index("uix_store_sku_inventory", "store_id", "sku_id", unique=True),
    )


class InventoryReservation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stock reservation hold associated with an order draft/checkout."""

    __tablename__ = "inventory_reservations"

    reservation_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sku_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="HELD", nullable=False, index=True)  # HELD | FULFILLED | RELEASED | EXPIRED
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class InventoryAuditLog(UUIDPrimaryKeyMixin, Base):
    """Immutable audit trail for inventory balance changes."""

    __tablename__ = "inventory_audit_logs"

    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sku_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)  # RESTOCK | RESERVE | DEDUCT | RELEASE
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    resulting_balance: Mapped[int] = mapped_column(Integer, nullable=False)
    performed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
