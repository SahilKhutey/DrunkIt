"""Cart database model."""

from __future__ import annotations

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import CartStatus


class Cart(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Shopping cart entity model."""

    __tablename__ = "carts"

    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[CartStatus] = mapped_column(
        Enum(CartStatus, name="cart_status"),
        default=CartStatus.ACTIVE,
        nullable=False,
    )
