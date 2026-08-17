from fastapi import APIRouter, HTTPException
from services.payment.app.api.payments import payment_service
from services.payment.app.schemas.refund import RefundRequest, RefundResponse
from services.payment.app.services.refund_service import RefundService

router = APIRouter(
    prefix="/refunds",
    tags=["Refunds"],
)

refund_service = RefundService(payment_service=payment_service)


@router.post("", response_model=RefundResponse)
async def create_refund(request: RefundRequest):
    try:
        refund = await refund_service.refund(
            payment_id=request.payment_id,
            amount=request.amount,
            idempotency_key=request.idempotency_key,
        )
        return RefundResponse(
            id=str(refund["id"]),
            payment_id=str(refund["payment_id"]),
            order_id=str(refund["order_id"]),
            amount=refund["amount"],
            status=refund["status"],
            provider_refund_id=refund.get("provider_refund_id"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
