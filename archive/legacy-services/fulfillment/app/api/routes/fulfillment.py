"""Fulfillment REST API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.database.session import get_db_session

from ...schemas.fulfillment import CreateFulfillmentRequest, FulfillmentResponse
from ...services.fulfillment_service import FulfillmentService

router = APIRouter(prefix="/fulfillments", tags=["fulfillment"])


@router.post(
    "",
    response_model=FulfillmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_fulfillment(
    request: CreateFulfillmentRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Create fulfillment and reserve inventory stock."""
    service = FulfillmentService(session)
    try:
        fulfillment = await service.create_fulfillment(
            request.order_id,
            request.warehouse_id,
            request.product_id,
            request.quantity,
        )
        await session.commit()
        await session.refresh(fulfillment)
        return FulfillmentResponse.model_validate(fulfillment)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/{fulfillment_id}/pick",
    response_model=FulfillmentResponse,
)
async def start_pick(
    fulfillment_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Start picking items for fulfillment."""
    service = FulfillmentService(session)
    fulfillment = await service.get(fulfillment_id)
    if not fulfillment:
        raise HTTPException(status_code=404, detail="Fulfillment not found")

    try:
        await service.start_picking(fulfillment)
        await session.commit()
        await session.refresh(fulfillment)
        return FulfillmentResponse.model_validate(fulfillment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{fulfillment_id}/pack",
    response_model=FulfillmentResponse,
)
async def pack(
    fulfillment_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Pack items for fulfillment."""
    service = FulfillmentService(session)
    fulfillment = await service.get(fulfillment_id)
    if not fulfillment:
        raise HTTPException(status_code=404, detail="Fulfillment not found")

    try:
        await service.pack(fulfillment)
        await session.commit()
        await session.refresh(fulfillment)
        return FulfillmentResponse.model_validate(fulfillment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{fulfillment_id}/ready",
    response_model=FulfillmentResponse,
)
async def mark_ready(
    fulfillment_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Mark fulfillment ready for carrier pickup."""
    service = FulfillmentService(session)
    fulfillment = await service.get(fulfillment_id)
    if not fulfillment:
        raise HTTPException(status_code=404, detail="Fulfillment not found")

    try:
        await service.mark_ready(fulfillment)
        await session.commit()
        await session.refresh(fulfillment)
        return FulfillmentResponse.model_validate(fulfillment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
