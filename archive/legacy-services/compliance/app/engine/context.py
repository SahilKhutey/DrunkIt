"""Eligibility context definition for rule engine evaluation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ConsumerContext(BaseModel):
    consumer_id: uuid.UUID | str
    age: int | None = None
    verified: bool = False
    verification_status: str | None = None


class ProductContext(BaseModel):
    product_id: uuid.UUID | str
    category: str | None = None
    alcohol_type: str | None = None
    abv: float | None = None
    quantity: int = 1


class LocationContext(BaseModel):
    country: str = "IN"
    state: str | None = None
    city: str | None = None


class OrderContext(BaseModel):
    total_quantity: int = 1
    total_value: float = 0.0


class EligibilityContext(BaseModel):
    consumer: ConsumerContext | None = None
    product: ProductContext | None = None
    location: LocationContext | None = None
    order: OrderContext = Field(default_factory=OrderContext)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Flat properties for legacy compatibility
    consumer_id: str | None = None
    retailer_id: str | None = None
    rider_id: str | None = None
    product_id: str | None = None
    order_id: str | None = None
    delivery_id: str | None = None
    jurisdiction_id: str | None = None
    operation: str | None = None
    consumer_verification_status: str | None = None

    model_config = ConfigDict(extra="allow")


# Alias for legacy compatibility
ComplianceContext = EligibilityContext
