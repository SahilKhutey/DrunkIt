from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, status

from faccp_common.dto import APIResponse
from app.api.dependencies import get_consumer_service
from app.schemas.consumer import (
    ProfileCreateRequest, ProfileResponse, ZKAgeClaimRequest, ZKAgeClaimResponse,
)
from app.services.consumer_service import ConsumerService

router = APIRouter(prefix="/consumer", tags=["Consumer Profiles"])


@router.post("/profiles", status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: ProfileCreateRequest,
    service: Annotated[ConsumerService, Depends(get_consumer_service)],
) -> APIResponse[ProfileResponse]:
    res = await service.create_profile(payload)
    return APIResponse(data=res)


@router.post("/zk-age-claim")
async def generate_zk_claim(
    payload: ZKAgeClaimRequest,
    service: Annotated[ConsumerService, Depends(get_consumer_service)],
) -> APIResponse[ZKAgeClaimResponse]:
    res = await service.generate_zk_claim(payload.consumer_id, payload.target_state)
    return APIResponse(data=res)
