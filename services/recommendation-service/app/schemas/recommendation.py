"""Recommendation service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PreferenceProfileCreate(BaseModel):
    consumer_id: str
    preferred_categories: list[str]
    preferred_brands: list[str]
    price_sensitivity_score: float = Field(ge=0.0, le=1.0)


class PreferenceProfileResponse(BaseModel):
    id: str
    consumer_id: str
    preferred_categories: list[str]
    preferred_brands: list[str]
    price_sensitivity_score: float
    updated_at: datetime


class AffinityScoreCreate(BaseModel):
    sku_id_a: str
    sku_id_b: str
    affinity_score: float = Field(ge=0.0, le=1.0)


class PersonalizedRecommendationResponse(BaseModel):
    consumer_id: str
    recommended_sku_ids: list[str]
    explanation: str
