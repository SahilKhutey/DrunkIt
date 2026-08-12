"""Payment service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class PaymentIntent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Payment intent for checkout processing."""

    __tablename__ = "payment_intents"

    order_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)

    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="CREATED", nullable=False, index=True)  # CREATED | CAPTURED | FAILED | REFUNDED
    gateway_provider: Mapped[str] = mapped_column(String(32), default="STUB_PAY", nullable=False)
    gateway_transaction_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    transactions: Mapped[list["PaymentTransaction"]] = relationship("PaymentTransaction", back_populates="intent", cascade="all, delete-orphan")


class PaymentTransaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Transaction log entry for gateway interactions."""

    __tablename__ = "payment_transactions"

    intent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("payment_intents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)  # AUTHORIZE | CAPTURE | REFUND
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # SUCCESS | FAILED

    intent: Mapped["PaymentIntent"] = relationship("PaymentIntent", back_populates="transactions")


class DoubleEntryLedger(UUIDPrimaryKeyMixin, Base):
    """Double-entry financial ledger recording debit/credit entries."""

    __tablename__ = "double_entry_ledgers"

    entry_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_debit: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_credit: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount_inr: Mapped[float] = mapped_column(Float, nullable=False)
    reference_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
