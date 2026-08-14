"""Risk evaluation result domain model."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from .enums import RiskDecision, RiskLevel


@dataclass
class RiskEvaluationResult:
    decision_id: uuid.UUID
    order_id: uuid.UUID
    decision: RiskDecision
    risk_level: RiskLevel
    score: float
    reasons: list[str] = field(default_factory=list)
    policy_version: str = "risk-v1"
