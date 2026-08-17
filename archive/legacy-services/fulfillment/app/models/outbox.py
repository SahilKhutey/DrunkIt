"""Fulfillment transactional outbox model."""

from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FulfillmentOutboxEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Fulfillment domain outbox table for atomic event emission."""

    __tablename__ = "fulfillment_outbox_events"

    event_type: Mapped[str] = mapped_column(String(150), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
