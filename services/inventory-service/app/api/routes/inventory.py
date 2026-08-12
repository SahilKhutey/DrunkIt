"""Inventory API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_inventory_service
from app.schemas.inventory import (
    DeductRequest, ReleaseRequest, ReservationRequest, ReservationResponse,
    StockResponse, StockUpdate,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory Engine"])


@router.post("/stock", response_model=SuccessResponse[StockResponse])
async def set_stock(
    payload: StockUpdate,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> SuccessResponse[StockResponse]:
    item = await service.set_stock(payload)
    return SuccessResponse(data=StockResponse(
        id=item.id, store_id=item.store_id, sku_id=item.sku_id,
        available_quantity=item.available_quantity,
        reserved_quantity=item.reserved_quantity,
        reorder_level=item.reorder_level, is_active=item.is_active,
    ), message="Stock balance updated")


@router.get("/stock/{store_id}/{sku_id}", response_model=SuccessResponse[StockResponse])
async def get_stock(
    store_id: str,
    sku_id: str,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> SuccessResponse[StockResponse]:
    item = await service.get_stock(store_id, sku_id)
    return SuccessResponse(data=StockResponse(
        id=item.id, store_id=item.store_id, sku_id=item.sku_id,
        available_quantity=item.available_quantity,
        reserved_quantity=item.reserved_quantity,
        reorder_level=item.reorder_level, is_active=item.is_active,
    ))


@router.post("/reserve", response_model=SuccessResponse[ReservationResponse], status_code=201)
async def reserve_stock(
    payload: ReservationRequest,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> SuccessResponse[ReservationResponse]:
    res = await service.reserve_stock(payload)
    return SuccessResponse(data=ReservationResponse(
        id=res.id, reservation_token=res.reservation_token,
        store_id=res.store_id, sku_id=res.sku_id, quantity=res.quantity,
        status=res.status, expires_at=res.expires_at,
    ), message="Stock reserved with TTL")


@router.post("/release", response_model=SuccessResponse[ReservationResponse])
async def release_reservation(
    payload: ReleaseRequest,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> SuccessResponse[ReservationResponse]:
    res = await service.release_reservation(payload)
    return SuccessResponse(data=ReservationResponse(
        id=res.id, reservation_token=res.reservation_token,
        store_id=res.store_id, sku_id=res.sku_id, quantity=res.quantity,
        status=res.status, expires_at=res.expires_at,
    ), message="Reservation released back to stock")


@router.post("/deduct", response_model=SuccessResponse[ReservationResponse])
async def deduct_reservation(
    payload: DeductRequest,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> SuccessResponse[ReservationResponse]:
    res = await service.deduct_reservation(payload)
    return SuccessResponse(data=ReservationResponse(
        id=res.id, reservation_token=res.reservation_token,
        store_id=res.store_id, sku_id=res.sku_id, quantity=res.quantity,
        status=res.status, expires_at=res.expires_at,
    ), message="Reservation deducted upon checkout completion")
