from fastapi import APIRouter, HTTPException
from services.delivery.app.schemas.dispatch import DispatchQueueRequest, DispatchJobResponse
from services.delivery.app.services.dispatch_service import DispatchService

router = APIRouter(
    prefix="/deliveries",
    tags=["Dispatch"],
)

dispatch_service = DispatchService()


@router.post("/{delivery_id}/dispatch", response_model=DispatchJobResponse)
async def queue_dispatch(
    delivery_id: str,
    payload: DispatchQueueRequest | None = None,
):
    priority = payload.priority if payload else 100
    try:
        job = await dispatch_service.queue_dispatch(delivery_id, priority=priority)
        return DispatchJobResponse(
            id=str(job["id"]),
            delivery_id=str(job["delivery_id"]),
            retailer_id=str(job["retailer_id"]),
            priority=job["priority"],
            status=job["status"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
