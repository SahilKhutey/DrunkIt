"""Compliance engine implementation."""

from __future__ import annotations

import uuid
from typing import Any, Sequence
from ..domain.decision import EligibilityDecision, RuleResult
from ..domain.enums import DecisionReasonCode, DecisionStatus
from .evaluator import evaluate_rule


class ComplianceEngine:
    """Deterministic compliance decision engine implementing fail-closed evaluation rules."""

    def evaluate(
        self,
        context: Any,
        policy: Any | None,
        rules: Sequence[Any],
        jurisdiction_id: uuid.UUID,
    ) -> EligibilityDecision:
        """Evaluate context against active policy rules."""
        # Fail-closed guard: No policy active for jurisdiction
        if policy is None:
            return EligibilityDecision(
                status=DecisionStatus.DENY,
                policy_id=None,
                jurisdiction_id=jurisdiction_id,
                results=[],
                reasons=["No active policy found for jurisdiction"],
                reason_codes=[DecisionReasonCode.NO_POLICY],
            )

        # Sort rules by priority ascending
        ordered_rules = sorted(
            [r for r in rules if getattr(r, "active", True)],
            key=lambda r: getattr(r, "priority", 100),
        )

        results: list[RuleResult] = []
        reasons: list[str] = []
        reason_codes: list[DecisionReasonCode] = []

        for rule in ordered_rules:
            res = evaluate_rule(rule, context)
            results.append(res)
            if not res.passed:
                reasons.append(res.reason)
                if res.reason_code and res.reason_code not in reason_codes:
                    reason_codes.append(res.reason_code)

        blocking_failures = [r for r in results if not r.passed and r.blocking]
        non_blocking_failures = [r for r in results if not r.passed and not r.blocking]

        if blocking_failures:
            status = DecisionStatus.DENY
        elif non_blocking_failures:
            status = DecisionStatus.REVIEW
        else:
            status = DecisionStatus.ALLOW

        return EligibilityDecision(
            status=status,
            policy_id=policy.id if hasattr(policy, "id") else None,
            jurisdiction_id=jurisdiction_id,
            results=results,
            reasons=reasons,
            reason_codes=reason_codes,
        )
