"""Trust verification — final gate for high-risk actions."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TrustThresholds:
    block: int = 20
    review: int = 50


class TrustOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    VERIFY = "VERIFY"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


@dataclass
class TrustDecision:
    outcome: TrustOutcome
    reason: str = ""
    confidence: float = 1.0
    checks_passed: list[str] = field(default_factory=list)
    signals: list[dict[str, Any]] = field(default_factory=list)
    requires: list[dict[str, Any]] = field(default_factory=list)
    review_id: str | None = None

    @property
    def is_allowed(self) -> bool:
        return self.outcome == TrustOutcome.ALLOW


class TrustDecisionEngine:
    """Evaluates whether an action should be allowed based on trust signals."""

    HIGH_RISK_ACTIONS = frozenset({
        "order:create", "payment:create", "payment:refund", "license:approve",
        "verification:approve", "policy:activate", "data:export",
    })

    BLOCK_THRESHOLD = 20
    REVIEW_THRESHOLD = 50
    MFA_REQUIRED_ROLES = frozenset({
        "SUPER_ADMIN", "REGULATORY_ADMIN", "STATE_ADMIN", "RETAILER_OWNER",
        "STORE_MANAGER", "DELIVERY_AGENT", "DATA_PROTECTION_OFFICER", "FINANCE_ADMIN",
    })

    async def evaluate(
        self,
        actor: Any,
        action: str,
        resource: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> TrustDecision:
        context = context or {}
        resource = resource or {}

        # Handle actor dictionary or AuthenticatedContext
        if isinstance(actor, dict):
            actor_dict = actor
        elif hasattr(actor, "to_dict") and callable(actor.to_dict):
            actor_dict = actor.to_dict()
        elif hasattr(actor, "identity"):
            if hasattr(actor.identity, "to_dict") and callable(actor.identity.to_dict):
                actor_dict = actor.identity.to_dict()
            elif isinstance(actor.identity, dict):
                actor_dict = actor.identity
            else:
                actor_dict = {"actor_id": getattr(actor, "user_id", "usr_0")}
        else:
            actor_dict = {"actor_id": getattr(actor, "user_id", "usr_0")}

        if hasattr(actor, "mfa_verified"):
            actor_dict["mfa_verified"] = actor.mfa_verified
        if hasattr(actor, "trust_score"):
            actor_dict["trust_score"] = actor.trust_score


        signals: list[dict[str, Any]] = []
        checks: list[str] = []

        # 1. Identity
        if actor_dict.get("status") in ("deleted", "suspended", "pending_deletion"):
            return TrustDecision(
                outcome=TrustOutcome.BLOCK,
                reason=f"Account {actor_dict.get('status')}",
            )
        if actor_dict.get("status") == "locked":
            return TrustDecision(TrustOutcome.DENY, "Account locked")
        checks.append("identity")

        # 2. Trust score
        trust = actor_dict.get("trust_score", 50)
        if trust < self.BLOCK_THRESHOLD:
            return TrustDecision(TrustOutcome.BLOCK, f"Trust score {trust} too low")
        if trust < self.REVIEW_THRESHOLD and action in self.HIGH_RISK_ACTIONS:
            return TrustDecision(TrustOutcome.REVIEW, f"Trust score {trust} requires review")
        signals.append({"type": "trust_score", "value": trust})
        checks.append("trust")

        # 3. Risk
        risk = actor_dict.get("risk_score", 0)
        if risk >= 80:
            return TrustDecision(TrustOutcome.BLOCK, f"Risk score {risk} critical")
        if risk >= 50 and action in self.HIGH_RISK_ACTIONS:
            return TrustDecision(TrustOutcome.REVIEW, f"Risk score {risk} elevated")
        signals.append({"type": "risk_score", "value": risk})
        checks.append("risk")

        # 4. MFA check (only if mfa_enabled is True and mfa_verified is False)
        if actor_dict.get("mfa_enabled") is True and not actor_dict.get("mfa_verified"):
            if action in self.HIGH_RISK_ACTIONS or actor_dict.get("primary_role") in self.MFA_REQUIRED_ROLES:
                return TrustDecision(
                    outcome=TrustOutcome.VERIFY,
                    reason="MFA required",
                    requires=[{"type": "MFA", "methods": ["totp", "sms", "hardware_key"]}],
                )
        checks.append("mfa")


        return TrustDecision(
            outcome=TrustOutcome.ALLOW,
            reason="All checks passed",
            confidence=min(1.0, trust / 100),
            checks_passed=checks,
            signals=signals,
        )
