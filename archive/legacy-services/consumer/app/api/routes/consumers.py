"""Consumer entity API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.database.session import get_db_session
from faccp_platform.security.principal import Principal
from ..deps import current_principal
from ...repositories.consumer import ConsumerRepository
from ...schemas.consumer import ConsumerCreate, ConsumerResponse
from ...services.consumer_service import ConsumerService

router = APIRouter(prefix="/consumers", tags=["consumers"])


@router.post(
    "",
    response_model=ConsumerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_consumer(
    request: ConsumerCreate,
    session: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(current_principal),
):
    """Create a new Consumer record for specified identity_id."""
    repository = ConsumerRepository(session)
    service = ConsumerService(repository, session=session)
    try:
        consumer = await service.create(request.identity_id)
        await session.commit()
        await session.refresh(consumer)
        return consumer
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "/{consumer_id}",
    response_model=ConsumerResponse,
)
async def get_consumer(
    consumer_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    principal: Principal = Depends(current_principal),
):
    """Fetch Consumer record by consumer_id with self-ownership authorization."""
    repository = ConsumerRepository(session)
    consumer = await repository.get(consumer_id)
    if consumer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found",
        )

    # Authorization Rule: self-ownership or administrative privilege
    if (
        str(principal.user_id) != str(consumer.identity_id)
        and not principal.has_permission("consumers:read:any")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return consumer
