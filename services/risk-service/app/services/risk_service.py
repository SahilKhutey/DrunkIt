from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RiskAssessment
from app.schemas.risk import RiskEvaluateRequest, RiskEvaluateResponse


class RiskService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def evaluate_risk(self, req: RiskEvaluateRequest) -> RiskEvaluateResponse:
        score = 0.1
        factors = {}

        if req.amount > 10000:
            score += 0.3
            factors["high_value_order"] = True

        if req.historical_order_count == 0:
            score += 0.2
            factors["first_time_buyer"] = True

        score = min(score, 1.0)
        level = "LOW"
        recommendation = "APPROVE"

        if score > 0.7:
            level = "HIGH"
            recommendation = "BLOCK"
        elif score > 0.4:
            level = "MEDIUM"
            recommendation = "MANUAL_REVIEW"

        assessment = RiskAssessment(
            subject_id=req.subject_id,
            subject_type=req.subject_type,
            risk_score=score,
            risk_level=level,
            risk_factors=factors,
            recommendation=recommendation,
        )
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)

        return RiskEvaluateResponse(
            id=assessment.id,
            subject_id=assessment.subject_id,
            subject_type=assessment.subject_type,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            recommendation=assessment.recommendation,
            risk_factors=assessment.risk_factors,
        )
