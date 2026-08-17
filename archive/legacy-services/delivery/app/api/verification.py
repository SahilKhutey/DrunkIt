from fastapi import APIRouter, HTTPException
from services.delivery.app.api.dispatch import dispatch_service
from services.delivery.app.schemas.verification import VerificationRequest, VerificationResult
from services.delivery.app.services.verification_service import VerificationService

router = APIRouter(
    prefix="/deliveries",
    tags=["Verification"],
)

verification_service = VerificationService(dispatch_service=dispatch_service)


@router.post("/{delivery_id}/verification/start")
async def start_verification(delivery_id: str):
    delivery = dispatch_service.deliveries.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="DELIVERY_NOT_FOUND")

    try:
        return await dispatch_service.transition(delivery, "VERIFICATION_PENDING")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{delivery_id}/verification/complete", response_model=VerificationResult)
async def complete_verification(delivery_id: str, payload: VerificationRequest):
    try:
        return await verification_service.verify_delivery(
            delivery_id=delivery_id,
            verification_token=payload.verification_token,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
