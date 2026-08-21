"""Commerce domain models for carts, cart items, orders, and order line items."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.catalog import SKU
    from app.models.retailer import RetailerLocation

# Use JSONB on PostgreSQL, fall back to JSON on SQLite/other
JsonType = JSONB().with_variant(JSON(), "sqlite")


class Cart(Base):
    """Consumer basket scoped to a user and optional target jurisdiction."""

    __tablename__ = "carts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    consumer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jurisdiction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jurisdictions.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
    )


class CartItem(Base):
    """Individual item inside a consumer cart."""

    __tablename__ = "cart_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    cart_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
    )
    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skus.id", ondelete="RESTRICT"),
        nullable=False,
    )
    retailer_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retailer_locations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_snapshot: Mapped[dict[str, Any]] = mapped_column(JsonType, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_cart_item_quantity_positive"),
    )

    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    sku: Mapped["SKU"] = relationship("SKU", foreign_keys=[sku_id])
    location: Mapped["RetailerLocation"] = relationship("RetailerLocation", foreign_keys=[retailer_location_id])


class Order(Base):
    """Authoritative order record with statutory compliance binding and idempotency protection."""

    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    consumer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    retailer_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retailer_locations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    subtotal_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    compliance_decision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("compliance_decisions.id", ondelete="RESTRICT"),
        nullable=True,
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("subtotal_minor >= 0", name="chk_order_subtotal_non_negative"),
        CheckConstraint("total_minor >= 0", name="chk_order_total_non_negative"),
        UniqueConstraint("consumer_id", "idempotency_key", name="uq_consumer_order_idempotency"),
    )

    # Relationships
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    location: Mapped["RetailerLocation"] = relationship("RetailerLocation", foreign_keys=[retailer_location_id])


class OrderItem(Base):
    """Line item in a confirmed order."""

    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skus.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_order_item_quantity_positive"),
        CheckConstraint("unit_price_minor >= 0", name="chk_order_item_price_non_negative"),
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    sku: Mapped["SKU"] = relationship("SKU", foreign_keys=[sku_id])
