"""
Continuous Trust Status (§14.5).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from .types import ActorType


class TrustStatus:
    """Continuously updated trust status for an actor."""

    def __init__(
        self,
        actor_id: str,
        actor_type: ActorType,
        base_score: int = 50,
        risk_score: int = 0,
        is_flagged: bool = False,
        is_blocked: bool = False,
        block_reason: str | None = None,
        last_updated: datetime | None = None,
    ) -> None:
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.base_score = base_score
        self.risk_score = risk_score
        self.is_flagged = is_flagged
        self.is_blocked = is_blocked
        self.block_reason = block_reason
        self.last_updated = last_updated or datetime.now(timezone.utc)

    @property
    def effective_trust_score(self) -> int:
        """Compute effective trust: base - risk."""
        return max(0, min(100, self.base_score - self.risk_score))

    @property
    def trust_level(self) -> str:
        if self.is_blocked:
            return "BLOCKED"
        score = self.effective_trust_score
        if score >= 90:
            return "EXCELLENT"
        if score >= 75:
            return "HIGH"
        if score >= 50:
            return "MEDIUM"
        if score >= 25:
            return "LOW"
        return "VERY_LOW"

    def can_perform_sensitive_action(self) -> bool:
        return not self.is_blocked and self.effective_trust_score >= 50

    def block(self, reason: str) -> None:
        self.is_blocked = True
        self.block_reason = reason
        self.last_updated = datetime.now(timezone.utc)

    def unblock(self) -> None:
        self.is_blocked = False
        self.block_reason = None
        self.last_updated = datetime.now(timezone.utc)
