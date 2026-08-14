"""Deterministic risk scoring engine."""

from __future__ import annotations

import uuid
from ..domain.decision import RiskEvaluationResult
from ..domain.enums import RiskDecision, RiskLevel
from ..schemas.risk import RiskEvaluationRequest
from .rules import (
    device_trust_rule,
    failed_payment_rule,
    high_amount_rule,
    order_velocity_rule,
)


class RiskScoringEngine:
    """Scoring engine mapping rule triggers into deterministic explainable decisions."""

    POLICY_VERSION = "risk-v1"

    def evaluate(self, request: RiskEvaluationRequest) -> RiskEvaluationResult:
        """Evaluate request against deterministic risk rules."""
        rules = [
            failed_payment_rule(request.failed_payments),
            order_velocity_rule(request.recent_order_count),
            device_trust_rule(request.device_trust_score),
            high_amount_rule(request.amount),
        ]

        triggered_rules = [r for r in rules if r.triggered]
        score = round(sum(r.score for r in triggered_rules), 2)
        reasons = [r.reason for r in triggered_rules]

        if score >= 0.70:
            decision = RiskDecision.BLOCK
            risk_level = RiskLevel.CRITICAL if score >= 0.85 else RiskLevel.HIGH
        elif score >= 0.35:
            decision = RiskDecision.REVIEW
            risk_level = RiskLevel.MEDIUM
        else:
            decision = RiskDecision.ALLOW
            risk_level = RiskLevel.LOW
            if not reasons:
                reasons = ["low_risk_baseline"]

        return RiskEvaluationResult(
            decision_id=uuid.uuid4(),
            order_id=request.order_id,
            decision=decision,
            risk_level=risk_level,
            score=score,
            reasons=reasons,
            policy_version=self.POLICY_VERSION,
        )
