"""Catalog service database models."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class Category(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Alcohol product category hierarchy."""

    __tablename__ = "categories"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)


class Brand(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Beverage brand entity."""

    __tablename__ = "brands"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(128), nullable=False)
    origin_country: Mapped[str] = mapped_column(String(2), default="IN", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)


class ProductMaster(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Canonical Product Master record."""

    __tablename__ = "product_masters"

    gtin: Mapped[str] = mapped_column(String(14), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("brands.id"), nullable=False, index=True
    )
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=False, index=True
    )

    volume_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    abv_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    packaging_type: Mapped[str] = mapped_column(String(32), default="GLASS_BOTTLE", nullable=False)  # GLASS_BOTTLE | CAN | TETRA | PET

    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    skus: Mapped[list["SKU"]] = relationship("SKU", back_populates="product", cascade="all, delete-orphan")


class SKU(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stock Keeping Unit under Product Master."""

    __tablename__ = "skus"

    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("product_masters.id", ondelete="CASCADE"), nullable=False, index=True
    )

    sku_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    barcode: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    pack_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    state_excise_code: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    product: Mapped["ProductMaster"] = relationship("ProductMaster", back_populates="skus")
    store_listings: Mapped[list["StoreListing"]] = relationship("StoreListing", back_populates="sku", cascade="all, delete-orphan")


class StoreListing(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Store-specific listing connecting SKU to a retail store with price."""

    __tablename__ = "store_listings"

    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sku_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("skus.id", ondelete="CASCADE"), nullable=False, index=True
    )

    mrp_inr: Mapped[float] = mapped_column(Float, nullable=False)
    selling_price_inr: Mapped[float] = mapped_column(Float, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    sku: Mapped["SKU"] = relationship("SKU", back_populates="store_listings")
