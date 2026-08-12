"""Inventory service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StockUpdate(BaseModel):
    store_id: str
    sku_id: str
    quantity: int = Field(gt=0)
    reorder_level: int = 5


class StockResponse(BaseModel):
    id: str
    store_id: str
    sku_id: str
    available_quantity: int
    reserved_quantity: int
    reorder_level: int
    is_active: bool


class ReservationRequest(BaseModel):
    store_id: str
    sku_id: str
    quantity: int = Field(gt=0)


class ReservationResponse(BaseModel):
    id: str
    reservation_token: str
    store_id: str
    sku_id: str
    quantity: int
    status: str
    expires_at: datetime


class ReleaseRequest(BaseModel):
    reservation_token: str


class DeductRequest(BaseModel):
    reservation_token: str
