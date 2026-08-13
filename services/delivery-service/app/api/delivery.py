from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.domain.delivery.enums import (
    ActorType,
    DeliveryStatus,
)
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryResponse,
    DriverAssignmentRequest,
    StatusTransitionRequest,
)
from app.services.delivery import DeliveryService


router = APIRouter(
    prefix="/deliveries",
    tags=["Deliveries"],
)


@router.post(
    "",
    response_model=DeliveryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_delivery(
    data: DeliveryCreate,
    session: AsyncSession = Depends(get_session),
):

    service = DeliveryService(session)

    try:
        return await service.create_delivery(data)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/{delivery_id}",
    response_model=DeliveryResponse,
)
async def get_delivery(
    delivery_id: str,
    session: AsyncSession = Depends(get_session),
):

    service = DeliveryService(session)

    delivery = await service.repository.get_by_id(
        delivery_id
    )

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found",
        )

    return delivery


@router.post(
    "/{delivery_id}/transition",
    response_model=DeliveryResponse,
)
async def transition_delivery(
    delivery_id: str,
    request: StatusTransitionRequest,
    session: AsyncSession = Depends(get_session),
):

    service = DeliveryService(session)

    delivery = await service.repository.get_by_id(
        delivery_id
    )

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found",
        )

    try:

        return await service.transition(
            delivery=delivery,
            target=request.target_status,
            actor_type=ActorType.SYSTEM,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.post(
    "/{delivery_id}/assign-driver",
    response_model=DeliveryResponse,
)
async def assign_driver(
    delivery_id: str,
    request: DriverAssignmentRequest,
    session: AsyncSession = Depends(get_session),
):

    service = DeliveryService(session)

    delivery = await service.repository.get_by_id(
        delivery_id
    )

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found",
        )

    try:

        return await service.assign_driver(
            delivery,
            request.driver_id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
