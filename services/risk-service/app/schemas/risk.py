"""Risk service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RiskEvaluationRequest(BaseModel):
    entity_type: str = Field(pattern="^(ORDER|CONSUMER|RETAILER)$")
    entity_id: str
    amount_inr: float = 0.0
    velocity_count_1h: int = 0
    is_new_device: bool = False


class RiskEvaluationResponse(BaseModel):
    id: str
    evaluation_code: str
    entity_type: str
    entity_id: str
    risk_score: float
    decision: str
    reason_codes: list[str]
    created_at: datetime


class FraudRuleCreate(BaseModel):
    rule_name: str = Field(min_length=3, max_length=64)
    description: str = Field(min_length=3, max_length=255)
    risk_score_impact: float = Field(ge=0.0, le=1.0)


class FraudRuleResponse(BaseModel):
    id: str
    rule_name: str
    description: str
    risk_score_impact: float
    is_active: bool
