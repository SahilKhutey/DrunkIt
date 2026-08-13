from fastapi import APIRouter, HTTPException
from services.order.app.api.checkout import checkout_service
from services.order.app.services.order_service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

order_service = OrderService(checkout_service=checkout_service)


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    customer_id: str | None = None,
):
    try:
        order = await order_service.get(order_id, customer_id=customer_id)
        if not order:
            raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")
        return order
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.post("/{order_id}/complete-payment")
async def complete_payment(
    order_id: str,
    payment_id: str,
):
    try:
        return await order_service.complete_payment(order_id, payment_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
