"""Compliance Policy API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.database.session import get_db_session
from ...schemas.policy import PolicyCreate, PolicyResponse
from ...services.policy_service import PolicyService

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post(
    "",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_policy(
    request: PolicyCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new compliance policy."""
    service = PolicyService(session)
    policy = await service.create(request)
    await session.commit()
    await session.refresh(policy)
    return policy


@router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
)
async def get_policy(
    policy_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch policy by ID."""
    service = PolicyService(session)
    policy = await service.get(policy_id)
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )
    return policy
