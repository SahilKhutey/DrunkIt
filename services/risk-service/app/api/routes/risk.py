"""Risk API routes."""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_risk_service
from app.schemas.risk import (
    FraudRuleCreate, FraudRuleResponse, RiskEvaluationRequest,
    RiskEvaluationResponse,
)
from app.services.risk_service import RiskService

router = APIRouter(prefix="/risk", tags=["Fraud Detection Engine"])


@router.post("/evaluate", response_model=SuccessResponse[RiskEvaluationResponse], status_code=201)
async def evaluate_risk(
    payload: RiskEvaluationRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
) -> SuccessResponse[RiskEvaluationResponse]:
    res = await service.evaluate_risk(payload)
    return SuccessResponse(data=RiskEvaluationResponse(
        id=res.id, evaluation_code=res.evaluation_code, entity_type=res.entity_type,
        entity_id=res.entity_id, risk_score=res.risk_score, decision=res.decision,
        reason_codes=json.loads(res.reason_codes_json), created_at=res.created_at,
    ), message=f"Risk evaluation complete: {res.decision}")


@router.post("/rules", response_model=SuccessResponse[FraudRuleResponse], status_code=201)
async def create_rule(
    payload: FraudRuleCreate,
    service: Annotated[RiskService, Depends(get_risk_service)],
) -> SuccessResponse[FraudRuleResponse]:
    rule = await service.create_rule(payload)
    return SuccessResponse(data=FraudRuleResponse(
        id=rule.id, rule_name=rule.rule_name, description=rule.description,
        risk_score_impact=rule.risk_score_impact, is_active=rule.is_active,
    ), message="Fraud rule created")


@router.get("/flagged", response_model=SuccessResponse[list[RiskEvaluationResponse]])
async def list_flagged(
    service: Annotated[RiskService, Depends(get_risk_service)],
) -> SuccessResponse[list[RiskEvaluationResponse]]:
    items = await service.list_flagged()
    return SuccessResponse(data=[RiskEvaluationResponse(
        id=r.id, evaluation_code=r.evaluation_code, entity_type=r.entity_type,
        entity_id=r.entity_id, risk_score=r.risk_score, decision=r.decision,
        reason_codes=json.loads(r.reason_codes_json), created_at=r.created_at,
    ) for r in items])
