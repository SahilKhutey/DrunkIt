"""Pydantic schemas for master catalog, brands, categories, products, variants, SKUs, and taste profiles."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base schema for category data."""

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    parent_id: uuid.UUID | None = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    pass


class CategoryResponse(CategoryBase):
    """Category representation in API responses."""

    id: uuid.UUID
    children: list["CategoryResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class BrandBase(BaseModel):
    """Base schema for brand data."""

    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str | None = None
    country_code: str | None = Field(default="IN", max_length=2)
    status: str = "ACTIVE"


class BrandCreate(BrandBase):
    """Schema for creating a brand."""

    pass


class BrandResponse(BrandBase):
    """Brand representation in API responses."""

    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TasteProfileSchema(BaseModel):
    """Taste metrics for flavor radar and recommendation matching."""

    body: Decimal | None = Field(default=None, ge=0, le=1)
    sweetness: Decimal | None = Field(default=None, ge=0, le=1)
    smokiness: Decimal | None = Field(default=None, ge=0, le=1)
    bitterness: Decimal | None = Field(default=None, ge=0, le=1)
    fruitiness: Decimal | None = Field(default=None, ge=0, le=1)
    spiciness: Decimal | None = Field(default=None, ge=0, le=1)
    confidence: Decimal | None = Field(default=None, ge=0, le=1)

    model_config = ConfigDict(from_attributes=True)


class ProductAttributeSchema(BaseModel):
    """Key-value attribute schema."""

    key: str = Field(min_length=1, max_length=100)
    value: str

    model_config = ConfigDict(from_attributes=True)


class SKUSchema(BaseModel):
    """Canonical SKU representation."""

    id: uuid.UUID
    canonical_code: str
    barcode: str | None = None
    status: str = "ACTIVE"

    model_config = ConfigDict(from_attributes=True)


class SKUCreate(BaseModel):
    """Schema for creating a canonical SKU."""

    canonical_code: str = Field(min_length=1, max_length=100)
    barcode: str | None = Field(default=None, max_length=100)


class ProductVariantSchema(BaseModel):
    """Product variant specification schema."""

    id: uuid.UUID
    volume_ml: int = Field(gt=0)
    packaging_type: str | None = "BOTTLE"
    package_count: int = Field(default=1, gt=0)
    status: str = "ACTIVE"
    skus: list[SKUSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProductVariantCreate(BaseModel):
    """Schema for creating a product variant."""

    volume_ml: int = Field(gt=0, description="Volume in milliliters (e.g. 750, 375, 180)")
    packaging_type: str = "BOTTLE"
    package_count: int = Field(default=1, gt=0)
    sku: SKUCreate | None = None


class ProductCreate(BaseModel):
    """Schema for creating a canonical product with variants and taste profile."""

    brand_id: uuid.UUID
    category_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str | None = None
    product_type: str = Field(default="WHISKY", description="WHISKY, GIN, VODKA, TEQUILA, RUM, RTD, BEER, WINE")
    region: str | None = None
    country_of_origin: str | None = "IN"
    abv: Decimal | None = Field(default=None, ge=0, le=100)
    variants: list[ProductVariantCreate] = Field(default_factory=list)
    attributes: list[ProductAttributeSchema] = Field(default_factory=list)
    taste_profile: TasteProfileSchema | None = None


class ProductSummaryResponse(BaseModel):
    """Concise product representation for listing and discovery feeds."""

    id: uuid.UUID
    brand_id: uuid.UUID
    brand_name: str | None = None
    category_id: uuid.UUID | None = None
    category_name: str | None = None
    name: str
    slug: str
    product_type: str
    region: str | None = None
    country_of_origin: str | None = None
    abv: Decimal | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductDetailResponse(ProductSummaryResponse):
    """Rich product representation with variants, SKUs, attributes, and taste profile."""

    description: str | None = None
    brand: BrandResponse | None = None
    category: CategoryResponse | None = None
    variants: list[ProductVariantSchema] = Field(default_factory=list)
    attributes: list[ProductAttributeSchema] = Field(default_factory=list)
    taste_profile: TasteProfileSchema | None = None


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    items: list[ProductSummaryResponse]
    total: int
    limit: int
    offset: int
