"""Payment transactional outbox model."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PaymentOutboxEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Payment domain outbox table for atomic event emission."""

    __tablename__ = "payment_outbox_events"

    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
