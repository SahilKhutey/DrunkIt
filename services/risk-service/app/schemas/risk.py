from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class EvaluateRequest(BaseModel):
    subject_type: str  # consumer|transaction|order|retailer
    subject_id: str
    context: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, Any]] | None = None


class EvaluateResponse(BaseModel):
    subject_type: str
    subject_id: str
    risk_score: int
    risk_level: str
    signals: list[dict[str, Any]] = Field(default_factory=list)


class EnhancedEvaluateRequest(BaseModel):
    subject_type: str  # consumer|transaction|order|retailer
    subject_id: str
    context: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, Any]] | None = None


class EnhancedEvaluateResponse(BaseModel):
    subject_type: str
    subject_id: str
    final_score: int
    level: str
    breakdown: dict[str, float]
    is_anomaly: bool
    top_contributors: list[dict[str, Any]]
    ato_signals: list[str]
    profile_id: str
    evaluated_at: datetime
    explanation: str


class RiskEvaluateRequest(BaseModel):
    subject_id: str
    subject_type: str = "ORDER"
    amount: float = 0.0
    device_fingerprint: str | None = None
    ip_address: str | None = None
    historical_order_count: int = 0


class RiskEvaluateResponse(BaseModel):
    id: str
    subject_id: str
    subject_type: str
    risk_score: float
    risk_level: str
    recommendation: str
    risk_factors: dict[str, Any]


class FraudCaseResponse(BaseModel):
    id: str
    case_number: str
    subject_type: str
    subject_id: str
    severity: str
    risk_score: int
    title: str


class ProfileResponse(BaseModel):
    id: str
    subject_type: str
    subject_id: str
    risk_score: int
    risk_level: str
