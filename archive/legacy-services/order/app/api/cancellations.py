from fastapi import APIRouter, HTTPException
from services.order.app.api.orders import order_service
from services.order.app.schemas.order import OrderCancellationRequest
from services.order.app.services.cancellation_service import CancellationService

router = APIRouter(
    prefix="/orders",
    tags=["Cancellations"],
)

cancellation_service = CancellationService(order_service=order_service)


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    payload: OrderCancellationRequest,
    customer_id: str | None = None,
):
    try:
        return await cancellation_service.cancel(
            order_id=order_id,
            reason=payload.reason,
            customer_id=customer_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
