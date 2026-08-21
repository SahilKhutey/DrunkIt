"""Pydantic schemas for Retailers, Locations, Licences, Inventory Snapshots, Pricing, and Live Availability."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class JurisdictionCreate(BaseModel):
    """Schema for creating a jurisdiction."""

    country_code: str = Field(default="IN", min_length=2, max_length=2)
    state_code: str | None = Field(default=None, max_length=10)
    name: str = Field(min_length=1, max_length=100)
    timezone: str = "Asia/Kolkata"


class JurisdictionResponse(BaseModel):
    """Jurisdiction representation schema."""

    id: uuid.UUID
    country_code: str
    state_code: str | None = None
    name: str
    timezone: str | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class RetailerCreate(BaseModel):
    """Schema for onboarding a retailer entity."""

    legal_name: str = Field(min_length=1, max_length=255)
    display_name: str = Field(min_length=1, max_length=255)


class RetailerResponse(BaseModel):
    """Retailer summary representation schema."""

    id: uuid.UUID
    legal_name: str
    display_name: str
    status: str
    licence_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RetailerLocationCreate(BaseModel):
    """Schema for creating a retailer store location."""

    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1)
    city: str = Field(min_length=1, max_length=100)
    state_code: str = Field(min_length=2, max_length=10)
    postal_code: str | None = None
    country_code: str = "IN"
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class RetailerLocationResponse(BaseModel):
    """Store location representation schema."""

    id: uuid.UUID
    retailer_id: uuid.UUID
    name: str
    address: str
    city: str
    state_code: str
    postal_code: str | None = None
    country_code: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class RetailerLicenceCreate(BaseModel):
    """Schema for registering an excise licence."""

    jurisdiction_id: uuid.UUID
    licence_number: str = Field(min_length=1, max_length=100)
    licence_type: str = Field(default="OFF_TRADE_RETAIL", description="OFF_TRADE_RETAIL, ON_TRADE, E_RETAIL")
    valid_from: date | None = None
    valid_to: date | None = None
    evidence_uri: str | None = None


class RetailerLicenceResponse(BaseModel):
    """Retailer licence representation schema."""

    id: uuid.UUID
    retailer_id: uuid.UUID
    jurisdiction_id: uuid.UUID
    licence_number: str
    licence_type: str
    valid_from: date | None = None
    valid_to: date | None = None
    status: str
    evidence_uri: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RetailerSKUMapRequest(BaseModel):
    """Schema for mapping a store POS item to a canonical SKU."""

    sku_id: uuid.UUID
    external_sku: str | None = None
    external_name: str = Field(min_length=1, max_length=255)


class RetailerSKUResponse(BaseModel):
    """Mapped Retailer SKU representation schema."""

    id: uuid.UUID
    retailer_location_id: uuid.UUID
    sku_id: uuid.UUID
    external_sku: str | None = None
    external_name: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class InventorySnapshotCreate(BaseModel):
    """Schema for ingesting an inventory snapshot."""

    retailer_sku_id: uuid.UUID
    quantity: int = Field(ge=0)
    availability_status: str = Field(default="IN_STOCK", description="IN_STOCK, LOW_STOCK, OUT_OF_STOCK")
    source: str = Field(default="POS_FEED", description="POS_FEED, MANUAL, API")
    source_reference: str | None = None


class InventorySnapshotResponse(BaseModel):
    """Inventory snapshot representation schema."""

    id: uuid.UUID
    retailer_sku_id: uuid.UUID
    quantity: int | None = None
    availability_status: str
    captured_at: datetime
    source: str

    model_config = ConfigDict(from_attributes=True)


class PriceCreate(BaseModel):
    """Schema for setting a price for a retailer SKU."""

    retailer_sku_id: uuid.UUID
    amount_minor: int = Field(ge=0, description="Price in paise / minor currency units (e.g. ₹1500.00 = 150000)")
    currency: str = "INR"
    effective_from: datetime | None = None
    effective_to: datetime | None = None


class PriceResponse(BaseModel):
    """Price representation schema."""

    id: uuid.UUID
    retailer_sku_id: uuid.UUID
    amount_minor: int
    currency: str
    effective_from: datetime
    effective_to: datetime | None = None
    captured_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ──────────────────────────────────────────────────────────────────────────────
# Availability Discovery Schemas
# ──────────────────────────────────────────────────────────────────────────────

class StoreAvailabilityItem(BaseModel):
    """Detailed availability entry for a specific store location."""

    retailer_id: uuid.UUID
    retailer_name: str
    location_id: uuid.UUID
    location_name: str
    address: str
    city: str
    state_code: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    distance_km: float | None = None
    sku_id: uuid.UUID
    canonical_code: str
    volume_ml: int
    availability_status: str
    quantity: int | None = None
    price_minor: int
    price_formatted: str
    currency: str = "INR"


class ProductAvailabilityResponse(BaseModel):
    """Aggregated availability response across stores for a product."""

    product_id: uuid.UUID
    product_name: str
    product_slug: str
    stores_count: int
    stores: list[StoreAvailabilityItem]
