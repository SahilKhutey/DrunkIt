"""Delivery and Verification REST API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.database.session import get_db_session

from ...domain.enums import DeliveryStatus, VerificationStatus
from ...schemas.delivery import CreateDeliveryRequest, DeliveryResponse
from ...schemas.verification import VerificationResponse, VerificationResult
from ...services.delivery_service import DeliveryService
from ...services.verification_service import VerificationService

router = APIRouter(prefix="/deliveries", tags=["delivery"])


@router.post(
    "",
    response_model=DeliveryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_delivery(
    request: CreateDeliveryRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Create delivery record for fulfillment."""
    service = DeliveryService(session)
    delivery = await service.create_delivery(request.order_id, request.fulfillment_id)
    await session.commit()
    await session.refresh(delivery)
    return DeliveryResponse.model_validate(delivery)


@router.post(
    "/{delivery_id}/assign",
    response_model=DeliveryResponse,
)
async def assign_courier(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Assign courier to delivery."""
    service = DeliveryService(session)
    delivery = await service.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    try:
        await service.assign_courier(delivery)
        await session.commit()
        await session.refresh(delivery)
        return DeliveryResponse.model_validate(delivery)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{delivery_id}/pickup",
    response_model=DeliveryResponse,
)
async def pickup(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Mark courier pickup for delivery."""
    service = DeliveryService(session)
    delivery = await service.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    try:
        await service.pickup(delivery)
        await session.commit()
        await session.refresh(delivery)
        return DeliveryResponse.model_validate(delivery)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{delivery_id}/arrived",
    response_model=DeliveryResponse,
)
async def arrived(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Mark courier arrival at customer location."""
    service = DeliveryService(session)
    delivery = await service.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    try:
        await service.arrived(delivery)
        await session.commit()
        await session.refresh(delivery)
        return DeliveryResponse.model_validate(delivery)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{delivery_id}/verification",
    response_model=VerificationResponse,
)
async def start_verification(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Start pending age/identity verification for delivery handoff."""
    delivery_service = DeliveryService(session)
    verification_service = VerificationService(session)

    delivery = await delivery_service.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    if delivery.status != DeliveryStatus.ARRIVED and delivery.status != DeliveryStatus.VERIFICATION_PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Delivery must be arrived to start verification",
        )

    if delivery.status == DeliveryStatus.ARRIVED:
        await delivery_service.arrived(delivery)

    verification = await verification_service.start(delivery.id)
    await session.commit()
    await session.refresh(verification)
    return VerificationResponse.model_validate(verification)


@router.post(
    "/verification/{verification_id}/complete",
    response_model=VerificationResponse,
)
async def complete_verification(
    verification_id: uuid.UUID,
    request: VerificationResult,
    session: AsyncSession = Depends(get_db_session),
):
    """Complete age/identity verification with pass or fail result."""
    verification_service = VerificationService(session)
    verification = await verification_service.get(verification_id)
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")

    try:
        res = await verification_service.complete(
            verification,
            passed=request.passed,
            method=request.method,
            reference=request.reference,
        )
        await session.commit()
        await session.refresh(res)
        return VerificationResponse.model_validate(res)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{delivery_id}/complete",
    response_model=DeliveryResponse,
)
async def complete_delivery(
    delivery_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Complete delivery handoff if verification passed, else transition to RETURNING."""
    delivery_service = DeliveryService(session)
    verification_service = VerificationService(session)

    delivery = await delivery_service.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    verification = await verification_service.get_by_delivery(delivery.id)
    if not verification:
        raise HTTPException(
            status_code=400,
            detail="Delivery verification record not found",
        )

    try:
        if verification.status == VerificationStatus.PASSED:
            await delivery_service.complete_delivery(delivery, verification)
        else:
            await delivery_service.fail_delivery(delivery)

        await session.commit()
        await session.refresh(delivery)
        return DeliveryResponse.model_validate(delivery)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
