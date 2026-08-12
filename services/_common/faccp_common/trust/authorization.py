"""Authorization engine — RBAC + ABAC combined."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AccessEffect(str, Enum):
    PERMIT = "PERMIT"
    DENY = "DENY"


@dataclass
class SubjectAttributes:
    user_id: str
    primary_role: str
    roles: list[str] = field(default_factory=list)
    organization_id: str | None = None
    assigned_stores: list[str] = field(default_factory=list)
    assigned_jurisdictions: list[str] = field(default_factory=list)
    mfa_enabled: bool = False
    mfa_verified: bool = False
    trust_score: int = 50
    risk_score: int = 0
    is_active: bool = True
    is_locked: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAttributes:
    resource_type: str
    resource_id: str | None = None
    owner_id: str | None = None
    organization_id: str | None = None
    classification: str = "P0"
    state: str | None = None
    store_id: str | None = None
    jurisdiction: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionAttributes:
    action: str
    is_sensitive: bool = False
    requires_mfa: bool = False
    requires_2man: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentAttributes:
    ip_address: str | None = None
    geo_country: str | None = None
    geo_state: str | None = None
    geo_city: str | None = None
    network_zone: str = "public"
    timestamp: str = ""
    user_agent: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    subject: SubjectAttributes
    resource: ResourceAttributes
    action: ActionAttributes
    environment: EnvironmentAttributes


@dataclass
class AccessDecision:
    effect: AccessEffect
    reason: str
    rule_id: str | None = None
    policy_id: str | None = None
    obligations: list[str] = field(default_factory=list)

    @property
    def is_permit(self) -> bool:
        return self.effect == AccessEffect.PERMIT

    @property
    def is_deny(self) -> bool:
        return self.effect == AccessEffect.DENY


class AuthorizationEngine:
    """RBAC + ABAC combined. Default-deny."""

    def __init__(self) -> None:
        # RBAC: role -> set of (resource_type, action) tuples
        self._rbac_matrix: dict[str, set[tuple[str, str]]] = {}
        # ABAC: list of (predicate, AccessDecision) rules
        self._abac_rules: list[tuple[str, callable, AccessDecision]] = []

    def register_rbac(self, role: str, resource_type: str, actions: list[str]) -> None:
        for action in actions:
            self._rbac_matrix.setdefault(role, set()).add((resource_type, action))

    def register_abac_rule(
        self, rule_id: str, predicate: callable, decision: AccessDecision
    ) -> None:
        self._abac_rules.append((rule_id, predicate, decision))

    def evaluate(self, request: AccessRequest) -> AccessDecision:
        # 1. Check if subject is active
        if not request.subject.is_active:
            return AccessDecision(AccessEffect.DENY, "Subject not active", rule_id="ACTIVE_CHECK")
        if request.subject.is_locked:
            return AccessDecision(AccessEffect.DENY, "Subject locked", rule_id="LOCK_CHECK")

        # 2. RBAC: does role grant (resource_type, action)?
        if not self._rbac_check(request):
            return AccessDecision(
                AccessEffect.DENY,
                f"Role '{request.subject.primary_role}' lacks '{request.action.action}' on '{request.resource.resource_type}'",
                rule_id="RBAC",
            )

        # 3. ABAC: resource-level checks
        abac_decision = self._abac_check(request)
        if abac_decision and abac_decision.effect == AccessEffect.DENY:
            return abac_decision

        # 4. MFA check for sensitive actions
        if request.action.requires_mfa and not request.subject.mfa_verified:
            return AccessDecision(
                AccessEffect.DENY,
                "MFA verification required",
                rule_id="MFA_CHECK",
            )

        # 5. Jurisdiction check
        if request.resource.jurisdiction:
            if request.subject.assigned_jurisdictions and (
                request.resource.jurisdiction not in request.subject.assigned_jurisdictions
                and not self._is_parent_jurisdiction(
                    request.resource.jurisdiction, request.subject.assigned_jurisdictions
                )
            ):
                return AccessDecision(
                    AccessEffect.DENY,
                    f"Subject not authorized in jurisdiction {request.resource.jurisdiction}",
                    rule_id="JURISDICTION_CHECK",
                )

        # 6. Store check
        if request.resource.store_id:
            if request.subject.assigned_stores and (
                request.resource.store_id not in request.subject.assigned_stores
            ):
                return AccessDecision(
                    AccessEffect.DENY,
                    f"Subject not assigned to store {request.resource.store_id}",
                    rule_id="STORE_CHECK",
                )

        return AccessDecision(AccessEffect.PERMIT, "All checks passed", rule_id="DEFAULT_PERMIT")

    def _rbac_check(self, request: AccessRequest) -> bool:
        for role in [request.subject.primary_role] + request.subject.roles:
            allowed = self._rbac_matrix.get(role, set())
            if (request.resource.resource_type, request.action.action) in allowed:
                return True
        return False

    def _abac_check(self, request: AccessRequest) -> AccessDecision | None:
        for rule_id, predicate, decision in self._abac_rules:
            try:
                if predicate(request):
                    return decision
            except Exception:
                logger.exception("abac_rule_failed", extra={"rule_id": rule_id})
        return None

    def _is_parent_jurisdiction(self, resource_jur: str, assigned: list[str]) -> bool:
        parts = resource_jur.split("-")
        for i in range(len(parts) - 1, 0, -1):
            parent = "-".join(parts[:i])
            if parent in assigned:
                return True
        return False


# Default engine with common RBAC grants
def default_authorization_engine() -> AuthorizationEngine:
    engine = AuthorizationEngine()
    # Consumer
    engine.register_rbac("CONSUMER", "order", ["create", "read:own", "cancel:own"])
    engine.register_rbac("CONSUMER", "profile", ["read:own", "update:own"])
    engine.register_rbac("CONSUMER", "verification", ["start"])
    # Store Manager
    engine.register_rbac("STORE_MANAGER", "inventory", ["read:own", "adjust"])
    engine.register_rbac("STORE_MANAGER", "order", ["read:own", "accept", "pack"])
    engine.register_rbac("STORE_MANAGER", "store", ["read:own", "update:own"])
    # Delivery Agent
    engine.register_rbac("DELIVERY_AGENT", "delivery", ["read:assigned", "complete"])
    engine.register_rbac("DELIVERY_AGENT", "location", ["update:own"])
    # Admin
    engine.register_rbac("SUPER_ADMIN", "*", ["*"])
    return engine
