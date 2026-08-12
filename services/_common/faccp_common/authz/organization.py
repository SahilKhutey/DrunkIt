"""
Organization Authorization (§16.5).
"""

from __future__ import annotations

from dataclasses import dataclass
from ..identity.types import Identity


@dataclass
class OrgDecision:
    allowed: bool
    reason: str | None = None


class OrganizationAuthZ:
    async def check(
        self,
        actor: Identity,
        resource_org_id: str | None,
        action: str,
        actor_org_id: str | None = None,
    ) -> OrgDecision:
        org_id = actor_org_id or getattr(actor, "organization_id", None)
        if actor.actor_type == "SYSTEM" or "SUPER_ADMIN" in actor.roles:
            return OrgDecision(allowed=True)

        if not resource_org_id:
            return OrgDecision(allowed=True)

        if org_id and org_id == resource_org_id:
            return OrgDecision(allowed=True)

        return OrgDecision(
            allowed=False,
            reason=f"Resource org '{resource_org_id}' does not match actor org '{org_id}'",
        )
