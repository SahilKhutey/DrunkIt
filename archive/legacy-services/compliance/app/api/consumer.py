from fastapi import APIRouter, HTTPException
from services.compliance.app.api.decisions import consumer_service
from services.compliance.app.schemas.compliance_schemas import ConsumerVerifyRequest

router = APIRouter(
    prefix="/compliance/consumer",
    tags=["Consumer Verification"],
)


@router.post("/{consumer_id}/verify")
async def verify_consumer(consumer_id: str, payload: ConsumerVerifyRequest | None = None):
    provider = payload.provider if payload else "ID_GOV_VERIFY"
    return await consumer_service.verify_consumer(consumer_id, provider=provider)


@router.get("/{consumer_id}/verification")
async def get_verification(consumer_id: str):
    res = await consumer_service.get_verification(consumer_id)
    if not res:
        raise HTTPException(status_code=404, detail="CONSUMER_VERIFICATION_NOT_FOUND")
    return res
