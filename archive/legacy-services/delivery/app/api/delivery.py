from fastapi import APIRouter, HTTPException
from services.delivery.app.api.dispatch import dispatch_service
from services.delivery.app.schemas.delivery import DeliveryCreate, DeliveryFailureRequest, DeliveryResponse
from services.delivery.app.services.delivery_service import DeliveryService
from services.delivery.app.services.pod_service import PodService

router = APIRouter(
    prefix="/deliveries",
    tags=["Delivery Operations"],
)

delivery_service = DeliveryService(dispatch_service=dispatch_service)
pod_service = PodService(delivery_service=delivery_service)


@router.post("", response_model=DeliveryResponse)
async def create_delivery(payload: DeliveryCreate):
    delivery = await dispatch_service.create_delivery(payload)
    return DeliveryResponse(
        id=str(delivery["id"]),
        order_id=str(delivery["order_id"]),
        status=delivery["status"],
        eta_seconds=delivery.get("eta_seconds"),
        verification_required=delivery["verification_required"],
    )


@router.get("/{delivery_id}")
async def get_delivery(delivery_id: str):
    delivery = await delivery_service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="DELIVERY_NOT_FOUND")
    return {
        "id": str(delivery["id"]),
        "order_id": str(delivery["order_id"]),
        "status": delivery["status"],
        "eta_seconds": delivery.get("eta_seconds"),
        "verification_required": delivery["verification_required"],
    }


@router.post("/{delivery_id}/pickup")
async def pickup(delivery_id: str):
    delivery = await delivery_service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="DELIVERY_NOT_FOUND")
    try:
        await dispatch_service.transition(delivery, "PICKUP_PENDING")
        return await dispatch_service.transition(delivery, "PICKED_UP")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{delivery_id}/in-transit")
async def in_transit(delivery_id: str):
    delivery = await delivery_service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="DELIVERY_NOT_FOUND")
    try:
        return await dispatch_service.transition(delivery, "IN_TRANSIT")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{delivery_id}/arriving")
async def arriving(delivery_id: str):
    delivery = await delivery_service.get_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="DELIVERY_NOT_FOUND")
    try:
        return await dispatch_service.transition(delivery, "ARRIVING")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{delivery_id}/handover")
async def handover(delivery_id: str):
    try:
        return await delivery_service.handover(delivery_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{delivery_id}/complete")
async def complete_delivery(delivery_id: str):
    try:
        return await pod_service.complete_delivery(delivery_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{delivery_id}/fail")
async def fail_delivery(delivery_id: str, payload: DeliveryFailureRequest):
    try:
        return await delivery_service.fail_delivery(delivery_id, reason=payload.reason, notes=payload.notes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{delivery_id}/return")
async def initiate_return(delivery_id: str):
    try:
        return await delivery_service.initiate_return(delivery_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
