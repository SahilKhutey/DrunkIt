from fastapi import APIRouter, HTTPException
from services.order.app.schemas.checkout import CheckoutRequest, CheckoutResponse
from services.order.app.services.checkout_service import CheckoutService

router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"],
)

checkout_service = CheckoutService()


@router.post("", response_model=CheckoutResponse)
async def checkout(
    request: CheckoutRequest,
):
    try:
        order = await checkout_service.checkout(request)
        return CheckoutResponse(
            order_id=str(order["id"]),
            status=order["status"],
            subtotal=order["subtotal"],
            taxes=order["taxes"],
            delivery_fee=order["delivery_fee"],
            discount=order["discount"],
            total=order["total"],
            currency=order["currency"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
