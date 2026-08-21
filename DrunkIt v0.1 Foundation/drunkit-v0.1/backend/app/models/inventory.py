"""Inventory and pricing domain models for retailer SKU mapping, stock snapshots, and temporal price integrity."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.catalog import SKU
    from app.models.retailer import RetailerLocation


class RetailerSKU(Base):
    """Mapping between a retailer store location and a canonical SKU."""

    __tablename__ = "retailer_skus"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    retailer_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retailer_locations.id", ondelete="CASCADE"),
        nullable=False,
    )
    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skus.id", ondelete="RESTRICT"),
        nullable=False,
    )
    external_sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")

    __table_args__ = (
        UniqueConstraint("retailer_location_id", "sku_id", name="uq_location_sku"),
    )

    # Relationships
    location: Mapped["RetailerLocation"] = relationship("RetailerLocation", foreign_keys=[retailer_location_id])
    sku: Mapped["SKU"] = relationship("SKU", foreign_keys=[sku_id])
    snapshots: Mapped[list["InventorySnapshot"]] = relationship(
        "InventorySnapshot",
        back_populates="retailer_sku",
        cascade="all, delete-orphan",
    )
    prices: Mapped[list["Price"]] = relationship(
        "Price",
        back_populates="retailer_sku",
        cascade="all, delete-orphan",
    )


class InventorySnapshot(Base):
    """Point-in-time inventory stock observation with freshness tracking."""

    __tablename__ = "inventory_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    retailer_sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retailer_skus.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    availability_status: Mapped[str] = mapped_column(String(50), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="chk_inventory_quantity_non_negative"),
        Index("idx_inventory_freshness", "retailer_sku_id", "captured_at"),
    )

    # Relationships
    retailer_sku: Mapped["RetailerSKU"] = relationship("RetailerSKU", back_populates="snapshots")


class Price(Base):
    """Temporal price record specifying statutory MRP and effective validity periods."""

    __tablename__ = "prices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    retailer_sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retailer_skus.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint("amount_minor >= 0", name="chk_price_amount_non_negative"),
        Index("idx_prices_active", "retailer_sku_id", "effective_from", "effective_to"),
    )

    # Relationships
    retailer_sku: Mapped["RetailerSKU"] = relationship("RetailerSKU", back_populates="prices")
