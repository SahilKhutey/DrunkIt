"""Cart Item database model."""

from __future__ import annotations

from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CartItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Shopping cart item model."""

    __tablename__ = "cart_items"

    cart_id: Mapped[str] = mapped_column(String(36), ForeignKey("carts.id"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
