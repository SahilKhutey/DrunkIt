"""Consumer Profile API routes."""

from __future__ import annotations

import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.database.session import get_db_session
from faccp_platform.security.principal import Principal
from ..deps import current_principal
from ...repositories.consumer import ConsumerRepository
from ...schemas.profile import ProfileResponse, ProfileUpdate
from ...services.profile_service import ProfileService

router = APIRouter(prefix="/consumers", tags=["profiles"])


@router.get(
    "/{consumer_id}/profile",
    response_model=ProfileResponse,
)
async def get_profile(
    consumer_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(current_principal),
):
    """Retrieve profile for specified consumer_id."""
    consumer_repo = ConsumerRepository(session)
    consumer = await consumer_repo.get(consumer_id)
    if consumer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found",
        )

    if (
        str(principal.user_id) != str(consumer.identity_id)
        and not principal.has_permission("consumer:profile:read")
        and not principal.has_permission("consumers:read:any")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    profile_service = ProfileService(session)
    profile = await profile_service.get(consumer_id)
    pref_dict = json.loads(profile.preferences_json) if profile and profile.preferences_json else {}

    return ProfileResponse(
        consumer_id=str(consumer_id),
        first_name=profile.first_name if profile else None,
        last_name=profile.last_name if profile else None,
        date_of_birth=profile.date_of_birth if profile else None,
        preferences=pref_dict,
    )


@router.patch(
    "/{consumer_id}/profile",
    response_model=ProfileResponse,
)
async def update_profile(
    consumer_id: uuid.UUID,
    request: ProfileUpdate,
    session: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(current_principal),
):
    """Update profile details for specified consumer_id."""
    consumer_repo = ConsumerRepository(session)
    consumer = await consumer_repo.get(consumer_id)
    if consumer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found",
        )

    if (
        str(principal.user_id) != str(consumer.identity_id)
        and not principal.has_permission("consumer:profile:update")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    profile_service = ProfileService(session)
    updated = await profile_service.update(consumer_id, request)
    await session.commit()
    await session.refresh(updated)

    pref_dict = json.loads(updated.preferences_json) if updated.preferences_json else {}
    return ProfileResponse(
        consumer_id=str(consumer_id),
        first_name=updated.first_name,
        last_name=updated.last_name,
        date_of_birth=updated.date_of_birth,
        preferences=pref_dict,
    )
