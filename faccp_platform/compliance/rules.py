"""Compliance rules and evaluation implementations."""

from __future__ import annotations

from typing import Any


class ComplianceRule:
    """Base compliance rule contract."""

    name: str = "base_rule"
    version: str = "1.0"

    def evaluate(self, context: Any) -> dict[str, Any]:
        """Evaluate rule against context. Return {'passed': bool, 'reason': str}."""
        raise NotImplementedError


class EligibilityRule(ComplianceRule):
    """Consumer regulatory eligibility rule."""

    name = "eligibility"
    version = "1.0"

    def evaluate(self, context: Any) -> dict[str, Any]:
        if isinstance(context, dict):
            eligible = context.get("eligible", True)
        else:
            eligible = getattr(context, "eligible", True)

        if not eligible:
            return {"passed": False, "reason": "eligibility_failed"}
        return {"passed": True}


class AgeVerificationRule(ComplianceRule):
    """Consumer legal age verification rule."""

    name = "age_verification"
    version = "1.0"

    def evaluate(self, context: Any) -> dict[str, Any]:
        if isinstance(context, dict):
            if "consumer_age" in context:
                age_verified = context["consumer_age"] >= 21
            else:
                age_verified = context.get("age_verified", True)
        else:
            if hasattr(context, "consumer_age"):
                age_verified = getattr(context, "consumer_age") >= 21
            else:
                age_verified = getattr(context, "age_verified", True)

        if not age_verified:
            return {"passed": False, "reason": "age_verification_failed"}
        return {"passed": True}
