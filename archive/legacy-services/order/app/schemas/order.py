"""Order DTO schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    product_name: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class CreateOrderRequest(BaseModel):
    consumer_id: uuid.UUID
    jurisdiction_id: uuid.UUID
    idempotency_key: str = Field(min_length=16, max_length=128)
    items: list[OrderItemCreate] = Field(min_length=1)
    discount: Decimal = Field(default=Decimal("0"), ge=0)
    tax: Decimal = Field(default=Decimal("0"), ge=0)
    delivery_fee: Decimal = Field(default=Decimal("0"), ge=0)

    # Optional compliance context overrides for testing/integrations
    consumer_age: int | None = None
    consumer_verified: bool = False
    consumer_verification_status: str | None = None
    state_code: str = "CG"
    city: str = "Bilaspur"


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name_snapshot: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    currency: str

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    consumer_id: uuid.UUID
    idempotency_key: str | None = None
    status: str
    payment_status: str
    fulfillment_status: str
    currency: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    delivery_fee: Decimal
    total: Decimal
    compliance_decision_id: uuid.UUID | None = None
    compliance_policy_version: str | None = None
    items: list[OrderItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
