"""Consumer profile database model."""

from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import Date, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import ProfileVisibility


class ConsumerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Consumer profile metadata model."""

    __tablename__ = "consumer_profiles"

    consumer_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    preferences_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    visibility: Mapped[ProfileVisibility] = mapped_column(
        Enum(ProfileVisibility, name="profile_visibility"),
        default=ProfileVisibility.STANDARD,
        nullable=False,
    )
