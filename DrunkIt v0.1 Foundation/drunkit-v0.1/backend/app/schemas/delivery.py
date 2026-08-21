"""Pydantic schemas for Delivery Driver Assignments and Statutory Handover Verification."""

import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class DeliveryAssignmentItem(BaseModel):
    """Order item summarized for driver manifest."""

    product_name: str = Field(default="", alias="product_name")
    volume_ml: int
    quantity: int
    unit_price_formatted: str


class DeliveryOrderManifest(BaseModel):
    """Driver delivery assignment manifest."""

    order_id: uuid.UUID
    retailer_name: str
    store_address: str
    customer_id: uuid.UUID
    delivery_channel: str
    status: str
    total_amount_formatted: str
    total_volume_ml: int
    items_summary: list[dict[str, Any]]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class DeliveryHandoverRequest(BaseModel):
    """Statutory doorstep handover submission by delivery driver."""

    otp: str = Field(min_length=4, max_length=6, description="4-6 digit delivery verification OTP")
    verified_id_type: Literal["AADHAAR", "PASSPORT", "DRIVING_LICENCE", "VOTER_ID"]
    recipient_declared_age: int = Field(ge=18, le=120)
    latitude: float | None = None
    longitude: float | None = None


class DeliveryHandoverResponse(BaseModel):
    """Delivery handover confirmation receipt."""

    order_id: uuid.UUID
    status: str
    handover_completed_at: str
    compliance_reference: str
    message: str


class DeliveryAbortRequest(BaseModel):
    """Statutory doorstep delivery cancellation and return to store."""

    reason: Literal["UNDERAGE_AT_DOOR", "NO_VALID_ID_PRESENTED", "CONSUMER_INTOXICATED", "ADDRESS_UNREACHABLE"]
    notes: str | None = None


class DeliveryAbortResponse(BaseModel):
    """Delivery cancellation receipt."""

    order_id: uuid.UUID
    status: str
    abort_reason: str
    aborted_at: str
    message: str
