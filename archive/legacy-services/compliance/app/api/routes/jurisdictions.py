"""Jurisdiction API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.database.session import get_db_session
from ...repositories.jurisdiction import JurisdictionRepository
from ...schemas.jurisdiction import JurisdictionCreate, JurisdictionResponse

router = APIRouter(prefix="/jurisdictions", tags=["jurisdictions"])


@router.post(
    "",
    response_model=JurisdictionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_jurisdiction(
    request: JurisdictionCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create or return existing jurisdiction."""
    repo = JurisdictionRepository(session)
    existing = await repo.get_by_code(request.country_code, request.state_code)
    if existing:
        return existing
    jurisdiction = await repo.create(request.country_code, request.state_code)
    await session.commit()
    await session.refresh(jurisdiction)
    return jurisdiction


@router.get(
    "/{jurisdiction_id}",
    response_model=JurisdictionResponse,
)
async def get_jurisdiction(
    jurisdiction_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch jurisdiction by ID."""
    repo = JurisdictionRepository(session)
    jurisdiction = await repo.get(jurisdiction_id)
    if jurisdiction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jurisdiction not found",
        )
    return jurisdiction
