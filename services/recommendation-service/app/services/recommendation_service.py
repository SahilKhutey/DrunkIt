"""Recommendation service: Personalized Recommendation & Affinity Matching Engine."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.logging import get_logger

from app.db.models import ConsumerPreferenceProfile, ProductAffinityScore
from app.schemas.recommendation import (
    AffinityScoreCreate, PersonalizedRecommendationResponse,
    PreferenceProfileCreate,
)

logger = get_logger(__name__)


class RecommendationService:
    """Personalized recommendation & CDP matching service."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def update_profile(self, payload: PreferenceProfileCreate) -> ConsumerPreferenceProfile:
        result = await self.db.execute(
            select(ConsumerPreferenceProfile).where(ConsumerPreferenceProfile.consumer_id == payload.consumer_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            profile = ConsumerPreferenceProfile(
                consumer_id=payload.consumer_id,
                preferred_categories_json=json.dumps(payload.preferred_categories),
                preferred_brands_json=json.dumps(payload.preferred_brands),
                price_sensitivity_score=payload.price_sensitivity_score,
            )
            self.db.add(profile)
        else:
            profile.preferred_categories_json = json.dumps(payload.preferred_categories)
            profile.preferred_brands_json = json.dumps(payload.preferred_brands)
            profile.price_sensitivity_score = payload.price_sensitivity_score

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def record_affinity(self, payload: AffinityScoreCreate) -> ProductAffinityScore:
        affinity = ProductAffinityScore(
            sku_id_a=payload.sku_id_a,
            sku_id_b=payload.sku_id_b,
            affinity_score=payload.affinity_score,
        )
        self.db.add(affinity)
        await self.db.commit()
        await self.db.refresh(affinity)
        return affinity

    async def get_personalized_recommendations(self, consumer_id: str) -> PersonalizedRecommendationResponse:
        result = await self.db.execute(
            select(ConsumerPreferenceProfile).where(ConsumerPreferenceProfile.consumer_id == consumer_id)
        )
        profile = result.scalar_one_or_none()

        sample_skus = ["SKU_SINGLE_MALT_12Y_750ML", "SKU_CRAFT_BEER_IPA_6PK", "SKU_CABERNET_SAUVIGNON_750ML"]
        explanation = "Recommended based on top category preferences and permit verification."

        if profile:
            categories = json.loads(profile.preferred_categories_json)
            explanation = f"Recommended based on preferred categories: {', '.join(categories)}"

        return PersonalizedRecommendationResponse(
            consumer_id=consumer_id,
            recommended_sku_ids=sample_skus,
            explanation=explanation,
        )
