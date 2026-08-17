"""Risk evaluation REST API routes."""

from __future__ import annotations

from fastapi import APIRouter
from ...schemas.risk import RiskEvaluationRequest, RiskEvaluationResponse
from ...services.scoring import RiskScoringEngine

router = APIRouter(prefix="/risk", tags=["risk"])
engine = RiskScoringEngine()


@router.post(
    "/evaluate",
    response_model=RiskEvaluationResponse,
)
async def evaluate_risk(request: RiskEvaluationRequest):
    """Evaluate order and transaction for financial/fraud risk."""
    result = engine.evaluate(request)
    return RiskEvaluationResponse(
        decision_id=result.decision_id,
        order_id=result.order_id,
        decision=result.decision,
        risk_level=result.risk_level,
        score=result.score,
        reasons=result.reasons,
        policy_version=result.policy_version,
    )
