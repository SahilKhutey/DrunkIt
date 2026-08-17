"""Cart DTO schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class AddToCartRequest(BaseModel):
    product_id: uuid.UUID
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)


class CartItemResponse(BaseModel):
    id: uuid.UUID
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: Decimal
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    id: uuid.UUID
    consumer_id: uuid.UUID
    status: str
    items: list[CartItemResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
