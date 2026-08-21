"""Pydantic schemas for Consumer Discovery, Occasions, and Semantic Taste Matching."""

import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalog import (
    BrandResponse,
    ProductSummaryResponse,
    TasteProfileSchema,
)


class OccasionCollection(BaseModel):
    """Curated occasion-based product collection."""

    slug: str
    title: str
    subtitle: str
    hero_tag: str
    item_count: int
    items: list[ProductSummaryResponse] = Field(default_factory=list)


class TasteMatchQuery(BaseModel):
    """Input query parameters for semantic taste matching and flavor radar."""

    body: Decimal | None = Field(default=None, ge=0, le=1, description="Desired body weight (0=light, 1=heavy)")
    sweetness: Decimal | None = Field(default=None, ge=0, le=1, description="Desired sweetness (0=dry, 1=sweet)")
    smokiness: Decimal | None = Field(default=None, ge=0, le=1, description="Desired peat/smoke (0=unpeated, 1=heavy peat)")
    bitterness: Decimal | None = Field(default=None, ge=0, le=1, description="Desired bitterness (0=smooth, 1=bitter/tannic)")
    fruitiness: Decimal | None = Field(default=None, ge=0, le=1, description="Desired fruit/floral notes (0=low, 1=high fruit)")
    spiciness: Decimal | None = Field(default=None, ge=0, le=1, description="Desired wood/botanical spice (0=mild, 1=spicy)")
    preferred_types: list[str] | None = Field(default=None, description="Filter by spirit types: WHISKY, GIN, TEQUILA, VODKA")
    min_abv: Decimal | None = Field(default=None, ge=0, le=100)
    max_abv: Decimal | None = Field(default=None, ge=0, le=100)
    limit: int = Field(default=10, ge=1, le=50)


class TasteMatchResult(BaseModel):
    """Similarity match result with product details and affinity score."""

    product: ProductSummaryResponse
    similarity_score: float = Field(ge=0, le=1.0, description="Cosine similarity score between 0.0 and 1.0")
    match_reasons: list[str] = Field(default_factory=list, description="Natural language reasons for the recommendation")
    taste_profile: TasteProfileSchema | None = None


class DiscoveryFeedResponse(BaseModel):
    """Root consumer discovery feed payload."""

    featured_brands: list[BrandResponse] = Field(default_factory=list)
    occasions: list[OccasionCollection] = Field(default_factory=list)
    spotlight_products: list[ProductSummaryResponse] = Field(default_factory=list)
