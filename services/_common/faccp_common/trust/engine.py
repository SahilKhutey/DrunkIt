"""
Trust Verification Decision Engine & Thresholds (Protocol 17).
Evaluates high-risk actions through 5 stages (Identity -> Eligibility -> Resource -> Policy -> Risk).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from ..auth.pipeline import AuthenticatedContext


class TrustOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    VERIFY = "VERIFY"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class TrustThresholds:
    HIGH_VALUE_ORDER = 10000
    VERY_HIGH_VALUE_ORDER = 50000
    BLOCK_THRESHOLD = 20
    VERIFY_THRESHOLD = 50
    ALERT_THRESHOLD = 75
    HIGH_RISK = 50
    CRITICAL_RISK = 80


@dataclass
class StageResult:
    outcome: str  # PASS | ALLOW | DENY | VERIFY | REVIEW | BLOCK
    confidence: float = 1.0
    reason: str = ""
    signals: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class TrustDecision:
    outcome: TrustOutcome
    confidence: float
    actor_id: str
    action: str
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    signals: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""
    requires: list[dict[str, Any]] = field(default_factory=list)
    review_id: str | None = None
    block_id: str | None = None
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TrustDecisionEngine:
    TRUST_REQUIRED_ACTIONS = frozenset({
        "order:create",
        "order:high_value",
        "payment:create",
        "payment:refund",
        "settlement:approve",
        "verification:approve",
        "license:approve",
        "license:revoke",
        "policy:activate",
        "admin:privilege_change",
        "data:export",
    })

    async def evaluate(
        self,
        actor: AuthenticatedContext,
        action: str,
        resource: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> TrustDecision:
        context = context or {}
        signals: list[dict[str, Any]] = []
        confidence = 1.0

        # Stage 1: Identity
        id_stage = self._check_identity(actor, action)
        signals.extend(id_stage.signals)
        if id_stage.outcome == "BLOCK":
            return TrustDecision(outcome=TrustOutcome.BLOCK, confidence=0.0, actor_id=actor.user_id, action=action, reason=id_stage.reason, signals=signals)
        if id_stage.outcome == "DENY":
            return TrustDecision(outcome=TrustOutcome.DENY, confidence=0.0, actor_id=actor.user_id, action=action, reason=id_stage.reason, signals=signals)
        if id_stage.outcome == "VERIFY":
            return TrustDecision(outcome=TrustOutcome.VERIFY, confidence=0.5, actor_id=actor.user_id, action=action, reason=id_stage.reason, signals=signals, requires=[{"type": "MFA"}])
        confidence *= id_stage.confidence

        # Stage 2: Eligibility
        el_stage = self._check_eligibility(actor, action, resource)
        signals.extend(el_stage.signals)
        if el_stage.outcome == "DENY":
            return TrustDecision(outcome=TrustOutcome.DENY, confidence=0.0, actor_id=actor.user_id, action=action, reason=el_stage.reason, signals=signals)
        if el_stage.outcome == "VERIFY":
            return TrustDecision(outcome=TrustOutcome.VERIFY, confidence=0.5, actor_id=actor.user_id, action=action, reason=el_stage.reason, signals=signals, requires=[{"type": "AGE_VERIFICATION"}])
        confidence *= el_stage.confidence

        # Stage 3: Resource
        res_stage = self._check_resource(actor, action, resource)
        signals.extend(res_stage.signals)
        if res_stage.outcome == "DENY":
            return TrustDecision(outcome=TrustOutcome.DENY, confidence=0.0, actor_id=actor.user_id, action=action, reason=res_stage.reason, signals=signals)

        # Stage 4: Policy
        pol_stage = self._check_policy(actor, action, resource)
        signals.extend(pol_stage.signals)
        if pol_stage.outcome == "DENY":
            return TrustDecision(outcome=TrustOutcome.DENY, confidence=0.0, actor_id=actor.user_id, action=action, reason=pol_stage.reason, signals=signals)

        # Stage 5: Risk
        risk_stage = self._check_risk(actor, action, context)
        signals.extend(risk_stage.signals)
        if risk_stage.outcome == "BLOCK":
            return TrustDecision(outcome=TrustOutcome.BLOCK, confidence=0.0, actor_id=actor.user_id, action=action, reason=risk_stage.reason, signals=signals)
        if risk_stage.outcome == "REVIEW":
            return TrustDecision(outcome=TrustOutcome.REVIEW, confidence=0.7, actor_id=actor.user_id, action=action, reason=risk_stage.reason, signals=signals, review_id="rev_12345")

        return TrustDecision(
            outcome=TrustOutcome.ALLOW,
            confidence=confidence,
            actor_id=actor.user_id,
            action=action,
            checks_passed=["identity", "eligibility", "resource", "policy", "risk"],
            signals=signals,
        )

    def _check_identity(self, actor: AuthenticatedContext, action: str) -> StageResult:
        signals = []
        if actor.trust_score < TrustThresholds.BLOCK_THRESHOLD:
            return StageResult(outcome="BLOCK", reason="Trust score critical", signals=[{"type": "low_trust"}])
        if actor.trust_score < TrustThresholds.VERIFY_THRESHOLD and action in self.TRUST_REQUIRED_ACTIONS:
            return StageResult(outcome="VERIFY", reason="Trust score requires re-verification", signals=[{"type": "trust_verify"}])
        return StageResult(outcome="PASS", confidence=actor.trust_score / 100.0, signals=signals)

    def _check_eligibility(self, actor: AuthenticatedContext, action: str, resource: dict[str, Any]) -> StageResult:
        signals = []
        if action.startswith("order:") and resource.get("product_type") == "alcohol":
            if actor.consumer_level not in {"C3_AGE_ELIGIBLE", "C4_TRANSACTION_VERIFIED"}:
                return StageResult(outcome="VERIFY", reason="Age verification required", signals=[{"type": "age_verify"}])
        return StageResult(outcome="PASS", confidence=1.0, signals=signals)

    def _check_resource(self, actor: AuthenticatedContext, action: str, resource: dict[str, Any]) -> StageResult:
        signals = []
        if resource.get("license", {}).get("status") == "EXPIRED":
            return StageResult(outcome="DENY", reason="License expired", signals=[{"type": "license_expired"}])
        return StageResult(outcome="PASS", confidence=1.0, signals=signals)

    def _check_policy(self, actor: AuthenticatedContext, action: str, resource: dict[str, Any]) -> StageResult:
        signals = []
        if resource.get("dry_day") is True:
            return StageResult(outcome="DENY", reason="Sale prohibited on dry day", signals=[{"type": "dry_day"}])
        return StageResult(outcome="PASS", confidence=1.0, signals=signals)

    def _check_risk(self, actor: AuthenticatedContext, action: str, context: dict[str, Any]) -> StageResult:
        signals = []
        if context.get("geo_impossible_travel"):
            return StageResult(outcome="BLOCK", reason="Impossible travel detected", signals=[{"type": "impossible_travel"}])
        if context.get("amount", 0) > TrustThresholds.VERY_HIGH_VALUE_ORDER:
            return StageResult(outcome="REVIEW", reason="High value transaction review", signals=[{"type": "high_value"}])
        return StageResult(outcome="PASS", confidence=1.0, signals=signals)
