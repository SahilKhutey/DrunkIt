"""Pydantic schemas for Cart, Compliance-Gated Checkout, and Order Lifecycle management."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CartItemAdd(BaseModel):
    """Payload to add or update an item in the active cart."""

    sku_id: uuid.UUID
    retailer_location_id: uuid.UUID
    quantity: int = Field(default=1, gt=0)


class CartItemResponse(BaseModel):
    """Cart item representation in API responses."""

    id: uuid.UUID
    sku_id: uuid.UUID
    canonical_code: str
    product_name: str
    volume_ml: int
    retailer_location_id: uuid.UUID
    retailer_name: str
    quantity: int
    unit_price_minor: int
    unit_price_formatted: str
    total_price_minor: int
    total_price_formatted: str

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    """Active shopping cart representation."""

    id: uuid.UUID
    consumer_id: uuid.UUID
    jurisdiction_id: uuid.UUID | None = None
    items: list[CartItemResponse] = Field(default_factory=list)
    item_count: int = 0
    subtotal_minor: int = 0
    subtotal_formatted: str = "₹0.00"
    total_volume_ml: int = 0
    status: str = "ACTIVE"

    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    """Payload to trigger compliance-gated checkout on active cart."""

    idempotency_key: str = Field(min_length=1, max_length=128, description="Client-generated unique UUID or string")
    channel: str = Field(default="ONLINE_ORDER", description="ONLINE_ORDER, IN_STORE, HOME_DELIVERY")
    consumer_age: int | None = Field(default=None, ge=0, le=120)
    is_age_verified: bool = False
    delivery_address: str | None = None
    current_time: datetime | None = None


class OrderItemResponse(BaseModel):
    """Line item in a placed order."""

    id: uuid.UUID
    sku_id: uuid.UUID
    canonical_code: str
    product_name: str
    volume_ml: int
    quantity: int
    unit_price_minor: int
    unit_price_formatted: str
    total_price_minor: int
    total_price_formatted: str

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Full order record representation."""

    id: uuid.UUID
    consumer_id: uuid.UUID
    retailer_location_id: uuid.UUID
    retailer_name: str
    status: str
    currency: str = "INR"
    subtotal_minor: int
    total_minor: int
    total_formatted: str
    compliance_decision_id: uuid.UUID | None = None
    idempotency_key: str
    items: list[OrderItemResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    """Payload to transition order lifecycle status."""

    status: str = Field(
        description="PENDING, CONFIRMED, PREPARING, READY_FOR_PICKUP, OUT_FOR_DELIVERY, FULFILLED, CANCELLED"
    )
