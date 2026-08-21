"""Retailer Portal API endpoints for bulk POS sync, order fulfillment, and store operations."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_sync_db
from app.db.uow import SyncUnitOfWork
from app.models.identity import User
from app.schemas.commerce import OrderResponse, OrderStatusUpdate
from app.schemas.retailer_portal import (
    BulkInventoryFeedRequest,
    BulkInventoryFeedResponse,
    RetailerStoreDashboardResponse,
    RetailerStoreOrdersResponse,
)
from app.services.retailer_portal_service import RetailerPortalService

router = APIRouter(prefix="/retailer", tags=["retailer-portal"])


@router.post(
    "/locations/{location_id}/inventory/bulk",
    response_model=BulkInventoryFeedResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk ingest POS inventory feed and price updates",
)
def bulk_ingest_inventory(
    location_id: uuid.UUID,
    request: BulkInventoryFeedRequest,
    current_user: User = Depends(require_roles("RETAILER", "ADMIN")),
    session: Session = Depends(get_sync_db),
) -> BulkInventoryFeedResponse:
    """Ingest bulk inventory snapshot feed and updated prices from store POS system."""
    uow = SyncUnitOfWork(session)
    with uow:
        result = RetailerPortalService.ingest_bulk_pos_feed(location_id, request, uow)
    return result


@router.get(
    "/locations/{location_id}/orders",
    response_model=RetailerStoreOrdersResponse,
    status_code=status.HTTP_200_OK,
    summary="List store orders for fulfillment",
)
def list_store_orders(
    location_id: uuid.UUID,
    status_filter: str | None = Query(None, alias="status", description="Filter by order status"),
    current_user: User = Depends(require_roles("RETAILER", "ADMIN")),
    session: Session = Depends(get_sync_db),
) -> RetailerStoreOrdersResponse:
    """Retrieve incoming order fulfillment queue for a specific physical store."""
    return RetailerPortalService.list_store_orders(location_id, session, status_filter)


@router.patch(
    "/locations/{location_id}/orders/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update store order fulfillment status",
)
def update_order_status(
    location_id: uuid.UUID,
    order_id: uuid.UUID,
    request: OrderStatusUpdate,
    current_user: User = Depends(require_roles("RETAILER", "ADMIN")),
    session: Session = Depends(get_sync_db),
) -> OrderResponse:
    """Transition order through fulfillment state machine (CONFIRMED -> PREPARING -> READY_FOR_PICKUP -> FULFILLED)."""
    uow = SyncUnitOfWork(session)
    with uow:
        updated_order = RetailerPortalService.update_store_order_status(
            location_id, order_id, request.status, uow, current_user.id
        )
    return updated_order


@router.get(
    "/locations/{location_id}/dashboard",
    response_model=RetailerStoreDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get real-time store dashboard analytics",
)
def get_store_dashboard(
    location_id: uuid.UUID,
    current_user: User = Depends(require_roles("RETAILER", "ADMIN")),
    session: Session = Depends(get_sync_db),
) -> RetailerStoreDashboardResponse:
    """Compute real-time SKU counts, stock health, and GMV analytics for a store location."""
    return RetailerPortalService.get_store_dashboard(location_id, session)
