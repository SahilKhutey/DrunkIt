"""
Persistence layer.

Deliberately mirrors the FACCP domain separation even at MVP scale:
Product (catalog truth) / Retailer+Store / Inventory / Price / Listing
(status only, not a copy of product data) / EligibilityVerification /
Order / Delivery are distinct tables. A single "big product row with
everything on it" is exactly what the original architecture warned
against, so we don't build that even for v1.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utcnow
from app.db.session import Base


def gen_id() -> str:
    return uuid.uuid4().hex


# ---------------------------------------------------------------------------
# Catalog (Product Master — truth, not presentation)
# ---------------------------------------------------------------------------

class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String, nullable=False)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)  # e.g. "beer", "whisky", "wine"
    variant: Mapped[str | None] = mapped_column(String, nullable=True)
    pack_size: Mapped[str] = mapped_column(String, nullable=False)  # "750 ml", "6x330ml"
    abv_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    listings: Mapped[list["Listing"]] = relationship(back_populates="product")


# ---------------------------------------------------------------------------
# Retailer / Store
# ---------------------------------------------------------------------------

class RetailerStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    SUSPENDED = "SUSPENDED"


class Retailer(Base):
    __tablename__ = "retailers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String, nullable=False)
    license_number: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[RetailerStatus] = mapped_column(
        Enum(RetailerStatus), default=RetailerStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    stores: Mapped[list["Store"]] = relationship(back_populates="retailer")

    @property
    def verified(self) -> bool:
        return self.status == RetailerStatus.VERIFIED


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    retailer_id: Mapped[str] = mapped_column(ForeignKey("retailers.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)  # jurisdiction key, e.g. "MAHARASHTRA"
    city: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    retailer: Mapped["Retailer"] = relationship(back_populates="stores")
    inventory_items: Mapped[list["InventoryItem"]] = relationship(back_populates="store")


# ---------------------------------------------------------------------------
# Inventory (separate from product; per-store quantity/state)
# ---------------------------------------------------------------------------

class InventoryStatus(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    __table_args__ = (UniqueConstraint("store_id", "product_id", name="uq_store_product"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=5)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )

    store: Mapped["Store"] = relationship(back_populates="inventory_items")
    product: Mapped["Product"] = relationship()

    @property
    def status(self) -> InventoryStatus:
        if self.quantity <= 0:
            return InventoryStatus.OUT_OF_STOCK
        if self.quantity <= self.low_stock_threshold:
            return InventoryStatus.LOW_STOCK
        return InventoryStatus.IN_STOCK


# ---------------------------------------------------------------------------
# Pricing (separate from product; per-store, authoritative for checkout)
# ---------------------------------------------------------------------------

class PriceRecord(Base):
    __tablename__ = "price_records"
    __table_args__ = (UniqueConstraint("store_id", "product_id", name="uq_price_store_product"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    mrp_paise: Mapped[int] = mapped_column(Integer, nullable=False)  # store money as integer paise
    selling_price_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )

    @property
    def discount_percentage(self) -> float:
        if self.mrp_paise <= 0:
            return 0.0
        return round((self.mrp_paise - self.selling_price_paise) / self.mrp_paise * 100, 1)


# ---------------------------------------------------------------------------
# Listing (status/lifecycle only — never a copy of product/price/inventory)
# ---------------------------------------------------------------------------

class ListingStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (UniqueConstraint("store_id", "product_id", name="uq_listing_store_product"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    status: Mapped[ListingStatus] = mapped_column(Enum(ListingStatus), default=ListingStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    product: Mapped["Product"] = relationship(back_populates="listings")
    store: Mapped["Store"] = relationship()


# ---------------------------------------------------------------------------
# Consumer / Eligibility
# ---------------------------------------------------------------------------

class EligibilityState(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class Consumer(Base):
    __tablename__ = "consumers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    phone: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)  # last known jurisdiction
    eligibility_state: Mapped[EligibilityState] = mapped_column(
        Enum(EligibilityState), default=EligibilityState.NOT_STARTED
    )
    eligibility_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class EligibilityCheckLog(Base):
    """
    Append-only audit trail. We do NOT store raw ID documents or
    biometric data here — only the decision, the policy version applied,
    and enough context to reconstruct why a decision was made.
    """
    __tablename__ = "eligibility_check_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    consumer_id: Mapped[str] = mapped_column(ForeignKey("consumers.id"), nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    minimum_age_required: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outcome: Mapped[EligibilityState] = mapped_column(Enum(EligibilityState), nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# ---------------------------------------------------------------------------
# Auth (phone + OTP). Kept deliberately separate from Consumer identity —
# an OTPChallenge is a short-lived proof attempt, a Session is a long-lived
# credential; neither belongs bolted onto the Consumer row.
# ---------------------------------------------------------------------------

class OTPChallenge(Base):
    __tablename__ = "otp_challenges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    phone: Mapped[str] = mapped_column(String, nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Session(Base):
    __tablename__ = "sessions"

    # The primary key IS the bearer token (a long random hex string) —
    # there's no separate "token" column to keep in sync with it.
    id: Mapped[str] = mapped_column(String, primary_key=True)
    consumer_id: Mapped[str] = mapped_column(ForeignKey("consumers.id"), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    consumer: Mapped["Consumer"] = relationship()


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

class OrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    ELIGIBILITY_REQUIRED = "ELIGIBILITY_REQUIRED"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    consumer_id: Mapped[str] = mapped_column(ForeignKey("consumers.id"), nullable=False)
    store_id: Mapped[str] = mapped_column(ForeignKey("stores.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.CREATED)

    subtotal_paise: Mapped[int] = mapped_column(Integer, default=0)
    delivery_fee_paise: Mapped[int] = mapped_column(Integer, default=0)
    total_paise: Mapped[int] = mapped_column(Integer, default=0)

    delivery_address: Mapped[str] = mapped_column(String, nullable=False)
    delivery_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_longitude: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    delivery: Mapped["Delivery | None"] = relationship(back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_paise: Mapped[int] = mapped_column(Integer, nullable=False)  # snapshot at order time

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()


# ---------------------------------------------------------------------------
# Delivery (kept separate from Order; an order can exist without one yet)
# ---------------------------------------------------------------------------

class DeliveryStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVING = "ARRIVING"
    HANDOFF_VERIFICATION = "HANDOFF_VERIFICATION"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False, unique=True)
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.REQUESTED)

    driver_name: Mapped[str | None] = mapped_column(String, nullable=True)
    driver_phone: Mapped[str | None] = mapped_column(String, nullable=True)

    eta_min_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    eta_max_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    handoff_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    failure_reason: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )

    order: Mapped["Order"] = relationship(back_populates="delivery")


class DeliveryEvent(Base):
    """Append-only event trail per delivery — cheap audit log for MVP."""
    __tablename__ = "delivery_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    delivery_id: Mapped[str] = mapped_column(ForeignKey("deliveries.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    detail: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
