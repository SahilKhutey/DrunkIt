"""Risk evaluation schemas."""

from __future__ import annotations

import uuid
from decimal import Decimal
from pydantic import BaseModel, Field
from ..domain.enums import RiskDecision, RiskLevel


class RiskEvaluationRequest(BaseModel):
    order_id: uuid.UUID
    consumer_id: uuid.UUID
    amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    product_count: int = Field(default=1, ge=1)
    delivery_distance_km: Decimal = Field(default=Decimal("0"), ge=0)
    account_age_days: int = Field(default=30, ge=0)
    previous_orders: int = Field(default=0, ge=0)
    failed_payments: int = Field(default=0, ge=0)
    recent_order_count: int = Field(default=0, ge=0)
    device_trust_score: float = Field(default=1.0, ge=0.0, le=1.0)


class RiskEvaluationResponse(BaseModel):
    decision_id: uuid.UUID
    order_id: uuid.UUID
    decision: RiskDecision
    risk_level: RiskLevel
    score: float
    reasons: list[str]
    policy_version: str
