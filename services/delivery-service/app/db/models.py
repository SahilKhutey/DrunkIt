"""Delivery & Dispatch Models."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class DeliveryTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "delivery_tasks"

    order_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    driver_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="UNASSIGNED", nullable=False)  # UNASSIGNED|ASSIGNED|PICKED_UP|DELIVERED
    otp_code: Mapped[str] = mapped_column(String(6), nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
