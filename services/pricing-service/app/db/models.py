"""
Pricing service models — price books, entries, promotions, tax rules, calculations.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Any
from sqlalchemy import Boolean, DateTime, Date, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class PriceBook(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "price_books"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    retailer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PriceBookEntry(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "price_book_entries"

    price_book_id: Mapped[str] = mapped_column(String(36), ForeignKey("price_books.id"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Promotion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "promotions"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    discount_type: Mapped[str] = mapped_column(String(16), nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    min_order_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    max_discount_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    applicable_categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    applicable_products: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    max_total_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_uses_per_user: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PromotionUsage(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "promotion_usage"

    promotion_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    discount_applied: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class PriceCalculation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "price_calculations"

    consumer_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    applied_promotion_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    line_items: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class TaxRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tax_rules"

    jurisdiction_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(16), default="GST", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
