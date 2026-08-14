"""Delivery DTO schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from ..domain.enums import DeliveryStatus


class CreateDeliveryRequest(BaseModel):
    order_id: uuid.UUID
    fulfillment_id: uuid.UUID


class DeliveryResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    fulfillment_id: uuid.UUID
    courier_id: uuid.UUID | None = None
    status: DeliveryStatus
    delivered_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
