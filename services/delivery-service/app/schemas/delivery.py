"""Delivery service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MissionCreate(BaseModel):
    order_id: str
    store_id: str
    consumer_id: str
    pickup_address: str = Field(min_length=3, max_length=255)
    dropoff_address: str = Field(min_length=3, max_length=255)


class MissionResponse(BaseModel):
    id: str
    mission_code: str
    order_id: str
    store_id: str
    consumer_id: str
    status: str
    pickup_address: str
    dropoff_address: str
    assigned_driver_id: str | None
    created_at: datetime


class DriverAssignRequest(BaseModel):
    driver_id: str


class LocationPingRequest(BaseModel):
    driver_id: str
    latitude: float
    longitude: float


class DeliveryCompleteRequest(BaseModel):
    otp: str = Field(min_length=4, max_length=6)
