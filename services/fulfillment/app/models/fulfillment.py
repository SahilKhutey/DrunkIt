"""Fulfillment database model."""

from __future__ import annotations

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import FulfillmentStatus


class Fulfillment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Warehouse fulfillment aggregate model."""

    __tablename__ = "fulfillments"

    order_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    warehouse_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[FulfillmentStatus] = mapped_column(
        Enum(FulfillmentStatus, name="fulfillment_status"),
        nullable=False,
        default=FulfillmentStatus.CREATED,
    )
