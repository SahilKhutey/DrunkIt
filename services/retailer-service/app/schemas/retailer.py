"""Retailer service API schemas."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    legal_name: str = Field(min_length=3, max_length=128)
    trade_name: str = Field(min_length=3, max_length=128)
    business_type: str = "PROPRIETORSHIP"
    gstin: str = Field(min_length=15, max_length=15)
    pan: str = Field(min_length=10, max_length=10)
    owner_user_id: str


class OrganizationResponse(BaseModel):
    id: str
    legal_name: str
    trade_name: str
    business_type: str
    gstin: str
    pan: str
    owner_user_id: str
    seller_level: str
    is_active: bool
    is_verified: bool
    created_at: datetime


class StoreCreate(BaseModel):
    organization_id: str
    code: str = Field(min_length=3, max_length=32)
    name: str = Field(min_length=3, max_length=128)
    store_type: str = "CL_2"
    address_line_1: str = Field(min_length=3, max_length=255)
    address_line_2: str | None = None
    city: str = Field(min_length=2, max_length=64)
    state: str = Field(min_length=2, max_length=64)
    pincode: str = Field(min_length=6, max_length=16)
    jurisdiction: str = Field(min_length=2, max_length=64)
    latitude: float
    longitude: float


class StoreResponse(BaseModel):
    id: str
    organization_id: str
    code: str
    name: str
    store_type: str
    address_line_1: str
    address_line_2: str | None
    city: str
    state: str
    pincode: str
    jurisdiction: str
    latitude: float
    longitude: float
    is_active: bool
    is_accepting_orders: bool
    created_at: datetime


class LicenseCreate(BaseModel):
    license_number: str = Field(min_length=3, max_length=64)
    license_type: str = "CL_2"
    issuing_authority: str = Field(min_length=3, max_length=128)
    jurisdiction: str = Field(min_length=2, max_length=64)
    valid_from: date
    valid_until: date
    document_url: str | None = None


class LicenseResponse(BaseModel):
    id: str
    store_id: str
    license_number: str
    license_type: str
    issuing_authority: str
    jurisdiction: str
    valid_from: date
    valid_until: date
    status: str
    document_url: str | None
    created_at: datetime


class StaffAssignCreate(BaseModel):
    user_id: str
    role_in_store: str = "STORE_MANAGER"


class StaffAssignResponse(BaseModel):
    id: str
    store_id: str
    user_id: str
    role_in_store: str
    is_active: bool
    created_at: datetime
