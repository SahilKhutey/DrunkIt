"""
Store Authorization (§16.6).
"""

from __future__ import annotations

from dataclasses import dataclass
from ..identity.types import Identity


@dataclass
class StoreDecision:
    allowed: bool
    reason: str | None = None


class StoreAuthZ:
    async def check(
        self,
        actor: Identity,
        store_id: str,
        action: str,
        assigned_stores: list[str] | None = None,
    ) -> StoreDecision:
        stores = assigned_stores or getattr(actor, "assigned_stores", [])
        if actor.actor_type in {"ADMIN", "SYSTEM", "AUDITOR"} or "SUPER_ADMIN" in actor.roles:
            return StoreDecision(allowed=True)

        if store_id in stores:
            return StoreDecision(allowed=True)

        return StoreDecision(
            allowed=False,
            reason=f"Store '{store_id}' not in assigned stores {stores}",
        )
