"""Processed payment webhook model."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProcessedPaymentWebhook(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Table tracking processed webhook event IDs for deduplication."""

    __tablename__ = "processed_payment_webhooks"

    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    event_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    payment_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processed")
