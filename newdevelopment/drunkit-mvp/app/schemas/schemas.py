from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# ---- Auth ----

class OTPRequestRequest(BaseModel):
    phone: str = Field(..., min_length=8, max_length=15)


class OTPRequestResponse(BaseModel):
    request_id: str
    expires_in_seconds: int
    dev_otp: Optional[str] = Field(
        None, description="Only populated outside production. Never rely on this in a real client."
    )


class OTPVerifyRequest(BaseModel):
    phone: str = Field(..., min_length=8, max_length=15)
    code: str = Field(..., min_length=6, max_length=6)


class OTPVerifyResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    consumer_id: str


# ---- Consumer / Eligibility ----

class MeResponse(BaseModel):
    consumer_id: str
    phone: str
    state: Optional[str]
    eligibility_state: str
    minimum_age_required: Optional[int] = None


class EligibilityVerifyRequest(BaseModel):
    state: str
    date_of_birth: date


class EligibilityVerifyResponse(BaseModel):
    decision: str
    can_view: bool
    can_add_to_cart: bool
    can_checkout: bool
    reason: str
    minimum_age_required: Optional[int]
    state: str


# ---- Listing ----

class PriceView(BaseModel):
    mrp: float
    selling_price: float
    discount_percentage: float


class ListingCardView(BaseModel):
    listing_id: str
    product_id: str
    name: str
    brand: str
    category: str
    variant: Optional[str]
    pack_size: str
    image_url: Optional[str]
    price: PriceView
    availability_status: str
    store_id: str
    store_name: str
    eta_min_minutes: int
    eta_max_minutes: int
    seller_verified: bool
    can_view: bool
    can_add_to_cart: bool
    eligibility_reason: str


# ---- Order ----

class CartLineIn(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class OrderCreateRequest(BaseModel):
    store_id: str
    items: list[CartLineIn]
    delivery_address: str
    delivery_latitude: float
    delivery_longitude: float


class OrderItemView(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float


class OrderView(BaseModel):
    id: str
    status: str
    subtotal: float
    delivery_fee: float
    total: float
    items: list[OrderItemView]


class OrderSummaryView(BaseModel):
    id: str
    status: str
    total: float
    item_count: int
    created_at: str


# ---- Delivery ----

class DeliveryTransitionRequest(BaseModel):
    new_status: str
    detail: Optional[str] = None


class HandoffVerifyRequest(BaseModel):
    verified: bool
    reason: Optional[str] = None


class DeliveryView(BaseModel):
    id: str
    order_id: str
    status: str
    eta_min_minutes: Optional[int]
    eta_max_minutes: Optional[int]
    handoff_verified: bool
    failure_reason: Optional[str]


# ---- Admin: catalog setup ----

class RetailerCreate(BaseModel):
    name: str
    license_number: Optional[str] = None


class StoreCreate(BaseModel):
    retailer_id: str
    name: str
    state: str
    city: str
    latitude: float
    longitude: float


class ProductCreate(BaseModel):
    name: str
    brand: str
    category: str
    variant: Optional[str] = None
    pack_size: str
    abv_percent: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


class ListingCreate(BaseModel):
    store_id: str
    product_id: str
    mrp: float
    selling_price: float
    quantity: int = 0

