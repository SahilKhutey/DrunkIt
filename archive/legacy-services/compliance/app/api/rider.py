from fastapi import APIRouter
from services.compliance.app.schemas.compliance_schemas import RiderAuthorizeRequest
from services.compliance.app.services.rider_service import RiderService

router = APIRouter(
    prefix="/compliance/rider",
    tags=["Rider Authorization"],
)

rider_service = RiderService()


@router.post("/{rider_id}/authorize")
async def authorize_rider(rider_id: str, payload: RiderAuthorizeRequest):
    return await rider_service.authorize_rider(
        rider_id=rider_id,
        jurisdiction_id=payload.jurisdiction_id,
        authorization_type=payload.authorization_type,
    )


@router.get("/{rider_id}/eligibility")
async def check_eligibility(rider_id: str, jurisdiction_id: str = "IN-STATE-X"):
    decision = await rider_service.get_eligibility(rider_id, jurisdiction_id)
    return {"rider_id": rider_id, "jurisdiction_id": jurisdiction_id, "decision": decision}
