"""Order service schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class OrderItemRequest(BaseModel):
    product_id: str
    sku: str
    product_name: str
    category: str
    brand: str | None = None
    abv: float | None = Field(default=None, ge=0, le=100)
    bottle_size_ml: int | None = Field(default=None, gt=0)
    quantity: int = Field(ge=1, le=100)
    unit_price: Decimal = Field(ge=0)


class CreateOrderRequest(BaseModel):
    consumer_id: str
    retailer_id: str
    store_id: str
    jurisdiction_code: str
    items: list[OrderItemRequest] = Field(min_length=1, max_length=100)
    delivery_address: dict[str, Any]
    delivery_zone: str | None = None
    delivery_instructions: str | None = Field(default=None, max_length=500)
    delivery_fee: Decimal = Field(default=Decimal("0"), ge=0)
    platform_fee: Decimal = Field(default=Decimal("0"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StateTransitionRequest(BaseModel):
    target_state: str
    reason: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OrderItemResponse(BaseModel):
    id: str
    product_id: str
    sku: str
    product_name: str
    category: str
    brand: str | None
    abv: float | None
    bottle_size_ml: int | None
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderResponse(BaseModel):
    id: str
    order_number: str
    state: str
    previous_state: str | None
    consumer_id: str
    retailer_id: str
    store_id: str
    driver_id: str | None
    subtotal: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    platform_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str
    jurisdiction_code: str
    compliance_decision: str | None
    delivery_address: dict[str, Any]
    delivery_zone: str | None
    estimated_delivery_at: datetime | None
    actual_delivery_at: datetime | None
    placed_at: datetime | None
    confirmed_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
