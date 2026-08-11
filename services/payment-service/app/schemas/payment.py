from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, Field

PaymentMethodStr = Literal["UPI", "CARD", "NET_BANKING", "WALLET", "BANK_TRANSFER"]


class CreateIntentRequest(BaseModel):
    order_id: str
    consumer_id: str
    retailer_id: str
    store_id: str
    amount: Decimal = Field(gt=0)
    currency: str = "INR"
    method: PaymentMethodStr
    platform_fee: Decimal = Field(default=Decimal("0"), ge=0)
    delivery_fee: Decimal = Field(default=Decimal("0"), ge=0)
    tax_amount: Decimal = Field(default=Decimal("0"), ge=0)
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntentResponse(BaseModel):
    id: str
    intent_number: str
    order_id: str
    amount: Decimal
    currency: str
    method: str
    status: str
    provider: str | None
    provider_intent_id: str | None
    provider_client_secret: str | None
    expires_at: datetime
    created_at: datetime


class AuthorizeRequest(BaseModel):
    provider_payment_id: str


class TransactionResponse(BaseModel):
    id: str
    transaction_number: str
    intent_id: str
    order_id: str
    amount: Decimal
    net_amount: Decimal
    currency: str
    method: str
    provider: str
    status: str
    captured_at: datetime


class RefundRequest(BaseModel):
    transaction_id: str
    amount: Decimal = Field(gt=0)
    reason: str = Field(min_length=5, max_length=500)


class RefundResponse(BaseModel):
    id: str
    refund_number: str
    transaction_id: str
    amount: Decimal
    reason: str
    status: str
    requires_2nd_approver: bool
    second_approved_at: datetime | None
    processed_at: datetime | None
    created_at: datetime


class WebhookPayload(BaseModel):
    event_id: str
    event_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: int = 0
