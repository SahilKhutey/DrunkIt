"""Order service models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now
from app.db.base import Base


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default="CREATED")
    previous_state: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Parties
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    retailer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    driver_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    # Amounts
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    # Compliance
    jurisdiction_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    compliance_decision_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    compliance_decision: Mapped[str | None] = mapped_column(String(16), nullable=True)  # allow|deny|review

    # Delivery
    delivery_address: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    delivery_zone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    delivery_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_delivery_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_delivery_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Lifecycle
    placed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    items: Mapped[list[OrderItem]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    state_history: Mapped[list[OrderStateHistory]] = relationship(
        "OrderStateHistory", back_populates="order", cascade="all, delete-orphan",
        order_by="OrderStateHistory.created_at"
    )

    __table_args__ = (
        Index("ix_order_consumer_state", "consumer_id", "state"),
        Index("ix_order_store_state", "store_id", "state"),
        Index("ix_order_retailer_state", "retailer_id", "state"),
    )


class OrderItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    product_name: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(128), nullable=True)
    abv: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    bottle_size_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    product_classification: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    order: Mapped[Order] = relationship("Order", back_populates="items")


class OrderStateHistory(UUIDPrimaryKeyMixin, Base):
    """Immutable history of every state transition."""
    __tablename__ = "order_state_history"

    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_state: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)  # user|system|driver|admin
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    order: Mapped[Order] = relationship("Order", back_populates="state_history")


class Cart(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "carts"

    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    jurisdiction_code: Mapped[str] = mapped_column(String(32), nullable=False, default="IN-KA")
    applied_promotion_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list[CartItem]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cart_items"

    cart_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    cart: Mapped[Cart] = relationship("Cart", back_populates="items")

