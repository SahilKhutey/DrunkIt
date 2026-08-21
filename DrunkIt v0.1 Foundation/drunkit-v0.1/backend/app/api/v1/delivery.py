"""Delivery API endpoints for mobile driver app, doorstep age check, and statutory returns."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_sync_db
from app.db.uow import SyncUnitOfWork
from app.models.identity import User
from app.schemas.delivery import (
    DeliveryAbortRequest,
    DeliveryAbortResponse,
    DeliveryHandoverRequest,
    DeliveryHandoverResponse,
    DeliveryOrderManifest,
)
from app.services.delivery_service import DeliveryService

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.get(
    "/assignments",
    response_model=list[DeliveryOrderManifest],
    status_code=status.HTTP_200_OK,
    summary="Get active delivery manifest assignments",
)
def list_delivery_assignments(
    session: Session = Depends(get_sync_db),
) -> list[DeliveryOrderManifest]:
    """Retrieve orders awaiting physical delivery dispatch or doorstep fulfillment."""
    return DeliveryService.list_assignments(session)


@router.post(
    "/orders/{order_id}/verify-and-complete",
    response_model=DeliveryHandoverResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify doorstep ID, validate OTP, and complete legal delivery handover",
)
def verify_and_complete_handover(
    order_id: uuid.UUID,
    request: DeliveryHandoverRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_sync_db),
) -> DeliveryHandoverResponse:
    """Execute statutory age verification and OTP confirmation at doorstep."""
    uow = SyncUnitOfWork(session)
    with uow:
        res = DeliveryService.verify_and_complete_handover(order_id, request, uow, current_user.id)
    return res


@router.post(
    "/orders/{order_id}/abort-statutory-return",
    response_model=DeliveryAbortResponse,
    status_code=status.HTTP_200_OK,
    summary="Abort delivery and initiate statutory return to licensed store",
)
def abort_delivery(
    order_id: uuid.UUID,
    request: DeliveryAbortRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_sync_db),
) -> DeliveryAbortResponse:
    """Fail-closed doorstep delivery cancellation when consumer is underage, intoxicated, or fails ID verification."""
    uow = SyncUnitOfWork(session)
    with uow:
        res = DeliveryService.abort_and_return_to_store(order_id, request, uow, current_user.id)
    return res
