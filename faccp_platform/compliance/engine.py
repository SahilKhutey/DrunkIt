"""Compliance Engine evaluating rules and outputting reproducible policy decisions."""

from __future__ import annotations

from typing import Any
from .decision import ComplianceDecision
from .rules import AgeVerificationRule, ComplianceRule, EligibilityRule


class ComplianceEngine:
    """Deterministic, auditable compliance evaluation engine."""

    def __init__(
        self,
        rules: list[ComplianceRule] | None = None,
        policy_version: str = "2026.08",
    ) -> None:
        self.rules = rules or [EligibilityRule(), AgeVerificationRule()]
        self.policy_version = policy_version

    def evaluate(self, context: Any) -> ComplianceDecision:
        """Evaluate context against rule suite and return policy decision."""
        failures: list[str] = []
        for rule in self.rules:
            res = rule.evaluate(context)
            if not res.get("passed", False):
                failures.append(res.get("reason", "unknown_failure"))

        if failures:
            return ComplianceDecision(
                allowed=False,
                state="rejected",
                reasons=failures,
                policy_version=self.policy_version,
            )

        return ComplianceDecision(
            allowed=True,
            state="verified",
            reasons=[],
            policy_version=self.policy_version,
        )
