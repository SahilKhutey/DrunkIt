from fastapi import APIRouter
from services.compliance.app.schemas.compliance_schemas import RetailerLicenseRequest
from services.compliance.app.services.retailer_service import RetailerService

router = APIRouter(
    prefix="/compliance/retailer",
    tags=["Retailer License"],
)

retailer_service = RetailerService()


@router.post("/{retailer_id}/license")
async def add_license(retailer_id: str, payload: RetailerLicenseRequest):
    return await retailer_service.add_license(
        retailer_id=retailer_id,
        license_number=payload.license_number,
        jurisdiction_id=payload.jurisdiction_id,
        license_type=payload.license_type,
        issuing_authority=payload.issuing_authority,
    )


@router.get("/{retailer_id}/eligibility")
async def check_eligibility(retailer_id: str, jurisdiction_id: str = "IN-STATE-X"):
    decision = await retailer_service.get_eligibility(retailer_id, jurisdiction_id)
    return {"retailer_id": retailer_id, "jurisdiction_id": jurisdiction_id, "decision": decision}
