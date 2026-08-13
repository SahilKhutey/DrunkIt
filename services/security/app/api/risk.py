from fastapi import APIRouter
from services.security.app.schemas.security_schemas import RiskEvaluationRequest
from services.security.app.services.risk_service import RiskService

router = APIRouter(
    prefix="/security",
    tags=["Risk Evaluation"],
)

risk_service = RiskService()


@router.post("/evaluate")
async def evaluate(request: RiskEvaluationRequest):
    return await risk_service.evaluate(
        subject_type=request.subject_type,
        subject_id=request.subject_id,
        operation=request.operation,
    )


@router.get("/risk/{subject_type}/{subject_id}")
async def get_risk(subject_type: str, subject_id: str):
    return await risk_service.evaluate(subject_type=subject_type, subject_id=subject_id)
