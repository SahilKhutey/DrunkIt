"""
Resource Ownership Checker (§16.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from ..identity.types import Identity


@dataclass
class OwnershipDecision:
    allowed: bool
    reason: str | None = None
    resource: Any = None


class ResourceOwnershipChecker:
    async def check(
        self,
        actor: Identity,
        resource_type: str,
        resource_id: str,
        action: str,
        resource_attrs: dict[str, Any] | None = None,
    ) -> OwnershipDecision:
        resource_attrs = resource_attrs or {}
        owner_id = resource_attrs.get("owner_id") or resource_attrs.get("consumer_id")

        if actor.actor_type == "SYSTEM" or "SUPER_ADMIN" in actor.roles:
            return OwnershipDecision(allowed=True)

        if owner_id and owner_id == actor.actor_id:
            return OwnershipDecision(allowed=True)

        if resource_attrs.get("organization_id") and resource_attrs["organization_id"] in getattr(actor, "organization_id", ""):
            return OwnershipDecision(allowed=True)

        return OwnershipDecision(
            allowed=False,
            reason=f"Actor {actor.actor_id} does not own {resource_type}:{resource_id}",
        )
