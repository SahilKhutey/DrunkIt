"""Courier database model."""

from __future__ import annotations

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Courier(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Delivery driver/courier entity model."""

    __tablename__ = "couriers"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
