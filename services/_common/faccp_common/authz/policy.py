"""
Compliance Policy Authorization (§16.7).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from ..identity.types import Identity


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str | None = None
    decision: str = "allow"


class PolicyAuthZ:
    async def check(
        self,
        actor: Identity,
        resource: dict[str, Any],
        action: str,
    ) -> PolicyDecision:
        # Default policy check passes unless prohibited
        if resource.get("prohibited_dry_day") is True:
            return PolicyDecision(allowed=False, reason="Sale prohibited on dry days", decision="deny")
        return PolicyDecision(allowed=True, reason="no_policy_violation", decision="allow")
