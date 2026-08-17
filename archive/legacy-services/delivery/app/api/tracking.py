from fastapi import APIRouter, HTTPException, WebSocket
from services.delivery.app.api.dispatch import dispatch_service
from services.delivery.app.schemas.tracking import LocationUpdate
from services.delivery.app.services.tracking_service import TrackingService

router = APIRouter(
    prefix="/deliveries",
    tags=["Tracking"],
)

tracking_service = TrackingService()


@router.get("/{delivery_id}/tracking")
async def get_tracking(delivery_id: str):
    events = tracking_service.tracking_events.get(delivery_id, [])
    delivery = dispatch_service.deliveries.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="DELIVERY_NOT_FOUND")

    return {
        "delivery_id": delivery_id,
        "status": delivery["status"],
        "eta_seconds": delivery.get("eta_seconds"),
        "rider": {"display_name": "Delivery Partner"},
        "tracking": {"enabled": True, "event_count": len(events)},
    }


@router.post("/{delivery_id}/tracking")
async def update_location(delivery_id: str, payload: LocationUpdate):
    event = await tracking_service.record_location(delivery_id, payload)
    if not event:
        raise HTTPException(status_code=400, detail="STALE_OR_OUT_OF_ORDER_GPS")
    return event


@router.websocket("/ws/{delivery_id}")
async def tracking_socket(websocket: WebSocket, delivery_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            payload = LocationUpdate(**data)
            await tracking_service.record_location(delivery_id, payload)
    except Exception:
        await websocket.close()
