"""Delivery API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_delivery_service
from app.schemas.delivery import (
    DeliveryCompleteRequest, DriverAssignRequest, LocationPingRequest,
    MissionCreate, MissionResponse,
)
from app.services.delivery_service import DeliveryService

router = APIRouter(prefix="/delivery", tags=["Fulfillment Engine"])


@router.post("/missions", response_model=SuccessResponse[MissionResponse], status_code=201)
async def create_mission(
    payload: MissionCreate,
    service: Annotated[DeliveryService, Depends(get_delivery_service)],
) -> SuccessResponse[MissionResponse]:
    mission, otp = await service.create_mission(payload)
    return SuccessResponse(data=MissionResponse(
        id=mission.id, mission_code=mission.mission_code, order_id=mission.order_id,
        store_id=mission.store_id, consumer_id=mission.consumer_id, status=mission.status,
        pickup_address=mission.pickup_address, dropoff_address=mission.dropoff_address,
        assigned_driver_id=mission.assigned_driver_id, created_at=mission.created_at,
    ), message=f"Mission created. OTP: {otp}")


@router.get("/missions/{mission_id}", response_model=SuccessResponse[MissionResponse])
async def get_mission(
    mission_id: str,
    service: Annotated[DeliveryService, Depends(get_delivery_service)],
) -> SuccessResponse[MissionResponse]:
    mission = await service.get_mission(mission_id)
    return SuccessResponse(data=MissionResponse(
        id=mission.id, mission_code=mission.mission_code, order_id=mission.order_id,
        store_id=mission.store_id, consumer_id=mission.consumer_id, status=mission.status,
        pickup_address=mission.pickup_address, dropoff_address=mission.dropoff_address,
        assigned_driver_id=mission.assigned_driver_id, created_at=mission.created_at,
    ))


@router.post("/missions/{mission_id}/assign", response_model=SuccessResponse[MissionResponse])
async def assign_driver(
    mission_id: str,
    payload: DriverAssignRequest,
    service: Annotated[DeliveryService, Depends(get_delivery_service)],
) -> SuccessResponse[MissionResponse]:
    mission = await service.assign_driver(mission_id, payload)
    return SuccessResponse(data=MissionResponse(
        id=mission.id, mission_code=mission.mission_code, order_id=mission.order_id,
        store_id=mission.store_id, consumer_id=mission.consumer_id, status=mission.status,
        pickup_address=mission.pickup_address, dropoff_address=mission.dropoff_address,
        assigned_driver_id=mission.assigned_driver_id, created_at=mission.created_at,
    ), message="Driver assigned to delivery mission")


@router.post("/missions/{mission_id}/ping", response_model=SuccessResponse[dict])
async def record_ping(
    mission_id: str,
    payload: LocationPingRequest,
    service: Annotated[DeliveryService, Depends(get_delivery_service)],
) -> SuccessResponse[dict]:
    ping = await service.record_ping(mission_id, payload)
    return SuccessResponse(data={
        "mission_id": ping.mission_id, "driver_id": ping.driver_id,
        "latitude": ping.latitude, "longitude": ping.longitude,
        "recorded_at": ping.recorded_at,
    }, message="Driver location ping recorded")


@router.post("/missions/{mission_id}/complete", response_model=SuccessResponse[MissionResponse])
async def complete_delivery(
    mission_id: str,
    payload: DeliveryCompleteRequest,
    service: Annotated[DeliveryService, Depends(get_delivery_service)],
) -> SuccessResponse[MissionResponse]:
    mission = await service.complete_delivery(mission_id, payload)
    return SuccessResponse(data=MissionResponse(
        id=mission.id, mission_code=mission.mission_code, order_id=mission.order_id,
        store_id=mission.store_id, consumer_id=mission.consumer_id, status=mission.status,
        pickup_address=mission.pickup_address, dropoff_address=mission.dropoff_address,
        assigned_driver_id=mission.assigned_driver_id, created_at=mission.created_at,
    ), message="Delivery completed & proof-of-delivery verified via OTP")
