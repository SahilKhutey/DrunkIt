from fastapi import APIRouter
from services.governance.app.services.governance_service import GovernanceService

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Compliance Reports"],
)

governance_service = GovernanceService()


@router.post("")
async def generate_report(report_type: str = "COMPLIANCE_AUDIT"):
    return await governance_service.generate_report(report_type=report_type)


@router.get("")
async def list_reports():
    rep = await governance_service.generate_report()
    return [rep]
