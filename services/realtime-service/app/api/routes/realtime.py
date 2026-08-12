"""Realtime API routes & WebSocket Endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_connection_manager
from app.schemas.realtime import BroadcastMessageRequest, ConnectionStatsResponse
from app.services.realtime_service import ConnectionManager

router = APIRouter(prefix="/realtime", tags=["Live Realtime Broadcasting"])


@router.websocket("/ws/orders/{order_id}")
async def order_stream(
    websocket: WebSocket,
    order_id: str,
    mgr: Annotated[ConnectionManager, Depends(get_connection_manager)],
) -> None:
    channel = f"order:{order_id}"
    await mgr.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        mgr.disconnect(channel, websocket)


@router.websocket("/ws/driver/{driver_id}")
async def driver_location_stream(
    websocket: WebSocket,
    driver_id: str,
    mgr: Annotated[ConnectionManager, Depends(get_connection_manager)],
) -> None:
    channel = f"driver:{driver_id}"
    await mgr.connect(channel, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        mgr.disconnect(channel, websocket)


@router.post("/broadcast", response_model=SuccessResponse[dict])
async def broadcast_message(
    payload: BroadcastMessageRequest,
    mgr: Annotated[ConnectionManager, Depends(get_connection_manager)],
) -> SuccessResponse[dict]:
    channel = f"{payload.topic}:{payload.channel_id}"
    await mgr.broadcast(channel, {"event_type": payload.event_type, "data": payload.data})
    return SuccessResponse(data={"channel": channel, "event_type": payload.event_type}, message="Message broadcast to WebSocket subscribers")


@router.get("/stats", response_model=SuccessResponse[ConnectionStatsResponse])
async def connection_stats(
    mgr: Annotated[ConnectionManager, Depends(get_connection_manager)],
) -> SuccessResponse[ConnectionStatsResponse]:
    channels, conns = mgr.get_stats()
    return SuccessResponse(data=ConnectionStatsResponse(active_channels=channels, total_connections=conns))
