from fastapi import APIRouter
from services.compliance.app.schemas.compliance import ComplianceContext, ComplianceDecision
from services.compliance.app.services.compliance_service import ComplianceService

router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"],
)

compliance_service = ComplianceService()


@router.post("/evaluate", response_model=ComplianceDecision)
async def evaluate_compliance(
    context: ComplianceContext,
):
    return await compliance_service.evaluate(context)
