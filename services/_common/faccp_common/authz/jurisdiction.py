"""
Jurisdiction Authorization (§16.4).
"""

from __future__ import annotations

from dataclasses import dataclass
from ..identity.types import Identity


@dataclass
class JurisdictionDecision:
    allowed: bool
    reason: str | None = None


class JurisdictionAuthZ:
    async def check(
        self,
        actor: Identity,
        resource_jurisdiction: str,
        action: str,
        assigned_jurisdictions: list[str] | None = None,
    ) -> JurisdictionDecision:
        jurisdictions = assigned_jurisdictions or getattr(actor, "assigned_jurisdictions", [])
        if actor.actor_type == "SYSTEM" or "SUPER_ADMIN" in actor.roles:
            return JurisdictionDecision(allowed=True)

        if not jurisdictions:
            return JurisdictionDecision(allowed=False, reason="Actor has no assigned jurisdictions")

        if resource_jurisdiction in jurisdictions:
            return JurisdictionDecision(allowed=True)

        # Parent matching (e.g. IN-KA matches IN-KA-BLR)
        for parent in jurisdictions:
            if resource_jurisdiction.startswith(parent):
                return JurisdictionDecision(allowed=True, reason=f"parent_match:{parent}")

        return JurisdictionDecision(
            allowed=False,
            reason=f"Jurisdiction {resource_jurisdiction} not in assigned jurisdictions {jurisdictions}",
        )
