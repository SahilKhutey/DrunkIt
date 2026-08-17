"""Payment DTO schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from ..domain.enums import PaymentMethodType, PaymentStatus


class CreatePaymentRequest(BaseModel):
    order_id: str
    consumer_id: str = ""
    customer_id: str | None = None
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    method: PaymentMethodType = Field(default=PaymentMethodType.UPI)
    idempotency_key: str = Field(min_length=16, max_length=128)

    def model_post_init(self, __context: Any) -> None:
        if self.customer_id and not self.consumer_id:
            object.__setattr__(self, "consumer_id", self.customer_id)


class CapturePaymentRequest(BaseModel):
    amount: Decimal | None = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: str
    consumer_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    method: PaymentMethodType
    provider: str
    provider_payment_id: str | None = None
    client_secret: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
