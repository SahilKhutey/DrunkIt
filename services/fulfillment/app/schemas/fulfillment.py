"""Fulfillment DTO schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from ..domain.enums import FulfillmentStatus


class CreateFulfillmentRequest(BaseModel):
    order_id: uuid.UUID
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int = 1


class FulfillmentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    warehouse_id: uuid.UUID
    status: FulfillmentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
