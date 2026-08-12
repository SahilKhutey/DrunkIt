"""
Unified Authorization Engine (§16.8).
Executes the full 7-step authorization pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from ..auth.pipeline import AuthenticatedContext
from .rbac import RBACEngine
from .ownership import ResourceOwnershipChecker
from .jurisdiction import JurisdictionAuthZ
from .organization import OrganizationAuthZ
from .store import StoreAuthZ
from .policy import PolicyAuthZ


@dataclass
class AuthorizationDecision:
    effect: str  # PERMIT | DENY
    checks_passed: list[str] = field(default_factory=list)
    failed_check: str | None = None
    reason: str | None = None
    actor_id: str | None = None
    action: str | None = None
    resource: str | None = None


class AuthorizationEngine:
    def __init__(
        self,
        rbac: RBACEngine | None = None,
        ownership: ResourceOwnershipChecker | None = None,
        jurisdiction: JurisdictionAuthZ | None = None,
        organization: OrganizationAuthZ | None = None,
        store: StoreAuthZ | None = None,
        policy: PolicyAuthZ | None = None,
    ) -> None:
        self.rbac = rbac or RBACEngine()
        self.ownership = ownership or ResourceOwnershipChecker()
        self.jurisdiction = jurisdiction or JurisdictionAuthZ()
        self.organization = organization or OrganizationAuthZ()
        self.store = store or StoreAuthZ()
        self.policy = policy or PolicyAuthZ()

    async def authorize(
        self,
        actor: AuthenticatedContext,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        resource_attrs: dict[str, Any] | None = None,
    ) -> AuthorizationDecision:
        resource_attrs = resource_attrs or {}
        checks_passed: list[str] = []

        # 1. RBAC Check
        rbac_dec = self.rbac.check(actor.roles, action)
        if not rbac_dec.allowed:
            return AuthorizationDecision(
                effect="DENY", failed_check="rbac", reason=rbac_dec.reason, actor_id=actor.user_id, action=action
            )
        checks_passed.append("rbac")

        # 2. Resource Ownership Check
        if resource_id:
            own_dec = await self.ownership.check(actor.identity, resource_type, resource_id, action, resource_attrs)
            if not own_dec.allowed:
                return AuthorizationDecision(
                    effect="DENY", failed_check="ownership", reason=own_dec.reason, actor_id=actor.user_id, action=action
                )
            checks_passed.append("ownership")

        # 3. Jurisdiction Check
        if resource_attrs.get("jurisdiction_code"):
            jur_dec = await self.jurisdiction.check(
                actor.identity, resource_attrs["jurisdiction_code"], action, actor.assigned_jurisdictions
            )
            if not jur_dec.allowed:
                return AuthorizationDecision(
                    effect="DENY", failed_check="jurisdiction", reason=jur_dec.reason, actor_id=actor.user_id, action=action
                )
            checks_passed.append("jurisdiction")

        # 4. Organization Check
        if resource_attrs.get("organization_id"):
            org_dec = await self.organization.check(
                actor.identity, resource_attrs["organization_id"], action, actor.organization_id
            )
            if not org_dec.allowed:
                return AuthorizationDecision(
                    effect="DENY", failed_check="organization", reason=org_dec.reason, actor_id=actor.user_id, action=action
                )
            checks_passed.append("organization")

        # 5. Store Check
        if resource_attrs.get("store_id"):
            st_dec = await self.store.check(
                actor.identity, resource_attrs["store_id"], action, actor.assigned_stores
            )
            if not st_dec.allowed:
                return AuthorizationDecision(
                    effect="DENY", failed_check="store", reason=st_dec.reason, actor_id=actor.user_id, action=action
                )
            checks_passed.append("store")

        # 6. Policy Check
        pol_dec = await self.policy.check(actor.identity, resource_attrs, action)
        if not pol_dec.allowed:
            return AuthorizationDecision(
                effect="DENY", failed_check="policy", reason=pol_dec.reason, actor_id=actor.user_id, action=action
            )
        checks_passed.append("policy")

        return AuthorizationDecision(
            effect="PERMIT",
            checks_passed=checks_passed,
            actor_id=actor.user_id,
            action=action,
            resource=f"{resource_type}:{resource_id}" if resource_id else resource_type,
        )
