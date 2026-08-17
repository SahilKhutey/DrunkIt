"""Jurisdiction database model."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Jurisdiction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Geographic/regulatory jurisdiction entity model."""

    __tablename__ = "jurisdictions"

    country_code: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    state_code: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
