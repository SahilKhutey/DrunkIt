"""Deterministic risk evaluation rules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class RiskRuleResult:
    triggered: bool
    score: float
    reason: str


def failed_payment_rule(failed_payments: int) -> RiskRuleResult:
    """Triggered on elevated failed payment velocity."""
    if failed_payments >= 5:
        return RiskRuleResult(
            triggered=True,
            score=0.40,
            reason="high_failed_payment_velocity",
        )
    if failed_payments >= 3:
        return RiskRuleResult(
            triggered=True,
            score=0.20,
            reason="elevated_failed_payment_velocity",
        )
    return RiskRuleResult(triggered=False, score=0.0, reason="")


def order_velocity_rule(recent_order_count: int) -> RiskRuleResult:
    """Triggered on rapid repeated ordering."""
    if recent_order_count >= 10:
        return RiskRuleResult(
            triggered=True,
            score=0.35,
            reason="excessive_order_velocity",
        )
    if recent_order_count >= 5:
        return RiskRuleResult(
            triggered=True,
            score=0.15,
            reason="elevated_order_velocity",
        )
    return RiskRuleResult(triggered=False, score=0.0, reason="")


def device_trust_rule(device_trust_score: float) -> RiskRuleResult:
    """Triggered on suspicious or untrusted device fingerprint."""
    if device_trust_score <= 0.2:
        return RiskRuleResult(
            triggered=True,
            score=0.35,
            reason="untrusted_device",
        )
    if device_trust_score <= 0.5:
        return RiskRuleResult(
            triggered=True,
            score=0.15,
            reason="low_device_trust",
        )
    return RiskRuleResult(triggered=False, score=0.0, reason="")


def high_amount_rule(amount: Decimal) -> RiskRuleResult:
    """Triggered on unusually high value transaction."""
    if amount >= Decimal("50000.00"):
        return RiskRuleResult(
            triggered=True,
            score=0.25,
            reason="high_value_transaction",
        )
    return RiskRuleResult(triggered=False, score=0.0, reason="")
