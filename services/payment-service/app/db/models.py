"""
Payment service — payment intents, transactions, refunds, ledger.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    EXPIRED = "EXPIRED"


class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"
    COD = "COD"
    BANK_TRANSFER = "BANK_TRANSFER"


class PaymentIntent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payment_intents"

    intent_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    retailer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    method: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default=PaymentStatus.PENDING.value, nullable=False, index=True)
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    provider_intent_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    provider_client_secret: Mapped[str | None] = mapped_column(String(256), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    authorized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class PaymentTransaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payment_transactions"

    transaction_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    intent_id: Mapped[str] = mapped_column(String(36), ForeignKey("payment_intents.id"), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    retailer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    method: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_transaction_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    provider_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    provider_tax: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class Refund(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "refunds"

    refund_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    transaction_id: Mapped[str] = mapped_column(String(36), ForeignKey("payment_transactions.id"), nullable=False, index=True)
    intent_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    retailer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    initiated_by: Mapped[str] = mapped_column(String(36), nullable=False)
    initiated_by_role: Mapped[str] = mapped_column(String(64), nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False, index=True)
    provider_refund_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_2nd_approver: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    second_approver_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    second_approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LedgerEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ledger_entries"

    entry_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    transaction_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("payment_transactions.id"), nullable=True, index=True)
    refund_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("refunds.id"), nullable=True, index=True)
    settlement_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    account_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_holder_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    debit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    credit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    description: Mapped[str] = mapped_column(String(256), nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class Settlement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "settlements"

    settlement_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    settlement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    holder_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    gross_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    fees: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    tax_withheld: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False, index=True)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    payout_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WebhookEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "webhook_events"

    provider: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    signature: Mapped[str | None] = mapped_column(String(512), nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
