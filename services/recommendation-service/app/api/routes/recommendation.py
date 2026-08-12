"""Recommendation API routes."""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_recommendation_service
from app.schemas.recommendation import (
    AffinityScoreCreate, PersonalizedRecommendationResponse,
    PreferenceProfileCreate, PreferenceProfileResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Personalized Discovery Engine"])


@router.post("/profiles", response_model=SuccessResponse[PreferenceProfileResponse], status_code=201)
async def update_profile(
    payload: PreferenceProfileCreate,
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
) -> SuccessResponse[PreferenceProfileResponse]:
    profile = await service.update_profile(payload)
    return SuccessResponse(data=PreferenceProfileResponse(
        id=profile.id, consumer_id=profile.consumer_id,
        preferred_categories=json.loads(profile.preferred_categories_json),
        preferred_brands=json.loads(profile.preferred_brands_json),
        price_sensitivity_score=profile.price_sensitivity_score,
        updated_at=profile.updated_at,
    ), message="Preference profile updated")


@router.post("/affinities", response_model=SuccessResponse[dict], status_code=201)
async def record_affinity(
    payload: AffinityScoreCreate,
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
) -> SuccessResponse[dict]:
    aff = await service.record_affinity(payload)
    return SuccessResponse(data={
        "sku_id_a": aff.sku_id_a, "sku_id_b": aff.sku_id_b, "affinity_score": aff.affinity_score,
    }, message="Product affinity score recorded")


@router.get("/personalized/{consumer_id}", response_model=SuccessResponse[PersonalizedRecommendationResponse])
async def get_personalized_recommendations(
    consumer_id: str,
    service: Annotated[RecommendationService, Depends(get_recommendation_service)],
) -> SuccessResponse[PersonalizedRecommendationResponse]:
    res = await service.get_personalized_recommendations(consumer_id)
    return SuccessResponse(data=res)
