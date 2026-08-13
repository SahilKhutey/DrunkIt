from fastapi import APIRouter, HTTPException
from services.payment.app.schemas.payment import CreatePaymentRequest, PaymentResponse
from services.payment.app.services.payment_service import PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)

payment_service = PaymentService()


@router.post("", response_model=PaymentResponse)
async def create_payment(request: CreatePaymentRequest):
    try:
        payment = await payment_service.create_payment(request)
        return PaymentResponse(
            id=str(payment["id"]),
            order_id=str(payment["order_id"]),
            customer_id=str(payment["customer_id"]),
            amount=payment["amount"],
            currency=payment["currency"],
            status=payment["status"],
            provider=payment["provider"],
            provider_payment_id=payment.get("provider_payment_id"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{payment_id}")
async def get_payment(payment_id: str):
    payment = payment_service.payments.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="PAYMENT_NOT_FOUND")
    return payment


@router.post("/{payment_id}/capture")
async def capture_payment(payment_id: str):
    try:
        return await payment_service.capture_payment(payment_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
