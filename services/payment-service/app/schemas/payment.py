"""Payment service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PaymentIntentCreate(BaseModel):
    order_id: str
    consumer_id: str
    amount_inr: float = Field(gt=0)
    gateway_provider: str = "STUB_PAY"


class PaymentIntentResponse(BaseModel):
    id: str
    order_id: str
    consumer_id: str
    amount_inr: float
    currency: str
    status: str
    gateway_provider: str
    gateway_transaction_id: str | None
    created_at: datetime


class PaymentCaptureRequest(BaseModel):
    gateway_transaction_id: str = Field(min_length=3, max_length=64)


class PaymentRefundRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=255)


class LedgerEntryResponse(BaseModel):
    id: str
    entry_id: str
    account_debit: str
    account_credit: str
    amount_inr: float
    reference_id: str
    created_at: datetime
