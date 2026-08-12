"""Order service API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    sku_id: str
    title: str = Field(min_length=1, max_length=255)
    unit_price_inr: float = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    consumer_id: str
    store_id: str
    delivery_address_id: str
    jurisdiction: str = Field(min_length=2, max_length=64)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    id: str
    sku_id: str
    title: str
    unit_price_inr: float
    quantity: int
    subtotal_inr: float


class OrderStateHistoryResponse(BaseModel):
    id: str
    from_state: str
    to_state: str
    triggered_by: str
    notes: str | None
    created_at: datetime


class OrderResponse(BaseModel):
    id: str
    order_number: str
    consumer_id: str
    store_id: str
    delivery_address_id: str
    jurisdiction: str
    order_state: str
    total_amount_inr: float
    delivery_fee_inr: float
    excise_tax_inr: float
    reservation_token: str | None
    payment_intent_id: str | None
    cancellation_reason: str | None
    items: list[OrderItemResponse]
    created_at: datetime


class OrderStateTransitionRequest(BaseModel):
    to_state: str
    notes: str | None = None


class OrderCancelRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=255)
