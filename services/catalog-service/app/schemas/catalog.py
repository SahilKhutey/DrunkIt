"""Catalog service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=64)
    description: str | None = None
    parent_id: str | None = None


class CategoryResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str | None
    parent_id: str | None
    is_active: bool


class BrandCreate(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=128)
    manufacturer: str = Field(min_length=2, max_length=128)
    origin_country: str = Field(default="IN", min_length=2, max_length=2)


class BrandResponse(BaseModel):
    id: str
    code: str
    name: str
    manufacturer: str
    origin_country: str
    is_active: bool


class ProductCreate(BaseModel):
    gtin: str = Field(min_length=12, max_length=14)
    title: str = Field(min_length=3, max_length=255)
    brand_id: str
    category_id: str
    volume_ml: int = Field(gt=0)
    abv_percentage: float = Field(ge=0, le=100)
    packaging_type: str = "GLASS_BOTTLE"
    image_url: str | None = None
    description: str | None = None


class ProductResponse(BaseModel):
    id: str
    gtin: str
    title: str
    brand_id: str
    category_id: str
    volume_ml: int
    abv_percentage: float
    packaging_type: str
    image_url: str | None
    description: str | None
    is_active: bool


class StoreListingCreate(BaseModel):
    store_id: str
    sku_id: str
    mrp_inr: float = Field(gt=0)
    selling_price_inr: float = Field(gt=0)
    is_available: bool = True


class StoreListingResponse(BaseModel):
    id: str
    store_id: str
    sku_id: str
    mrp_inr: float
    selling_price_inr: float
    is_available: bool
