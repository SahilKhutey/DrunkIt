"""Order service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Regulatory Order entity governed by the State Machine."""

    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    delivery_address_id: Mapped[str] = mapped_column(String(36), nullable=False)

    jurisdiction: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    order_state: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False, index=True)

    total_amount_inr: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_fee_inr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    excise_tax_inr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    reservation_token: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    payment_intent_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    state_history: Mapped[list["OrderStateHistory"]] = relationship("OrderStateHistory", back_populates="order", cascade="all, delete-orphan")
    compliance_record: Mapped["ComplianceValidationRecord | None"] = relationship("ComplianceValidationRecord", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Line item in a regulatory order."""

    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price_inr: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal_inr: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")


class OrderStateHistory(UUIDPrimaryKeyMixin, Base):
    """Audit log of order state machine transitions."""

    __tablename__ = "order_state_histories"

    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_state: Mapped[str] = mapped_column(String(32), nullable=False)
    to_state: Mapped[str] = mapped_column(String(32), nullable=False)
    triggered_by: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="state_history")


class ComplianceValidationRecord(UUIDPrimaryKeyMixin, Base):
    """Compliance verification proof attached to the order."""

    __tablename__ = "compliance_validation_records"

    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    is_compliant: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evaluation_id: Mapped[str] = mapped_column(String(64), nullable=False)
    rules_checked: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="compliance_record")
