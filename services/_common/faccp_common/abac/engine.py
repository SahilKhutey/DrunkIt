"""
ABAC engine — evaluates access requests against policy rules.

This implements a focused subset of XACML/ALFA-style ABAC:
- Subject attributes (user, roles, claims)
- Resource attributes (type, owner, classification)
- Action attributes (type, sensitivity)
- Environment attributes (time, location, device)
- Rules with conditions combined via AND/OR
- Permit / Deny / NotApplicable decisions
- Combining algorithm: deny-overrides (default)
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class PolicyEffect(str, Enum):
    PERMIT = "PERMIT"
    DENY = "DENY"


@dataclass
class SubjectAttributes:
    user_id: str
    primary_role: str
    roles: list[str]
    organization_id: str | None = None
    assigned_stores: list[str] = field(default_factory=list)
    assigned_jurisdictions: list[str] = field(default_factory=list)
    mfa_verified: bool = False
    device_trust_score: int = 50
    risk_score: int = 0
    is_locked: bool = False
    is_active: bool = True
    custom: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAttributes:
    resource_type: str
    resource_id: str | None = None
    owner_id: str | None = None
    organization_id: str | None = None
    classification: str = "P0"  # P0|P1|P2|P3
    state: str | None = None
    store_id: str | None = None
    jurisdiction: str | None = None
    custom: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionAttributes:
    action: str  # create|read|update|delete|verify|approve|export
    is_sensitive: bool = False
    requires_mfa: bool = False
    requires_2man: bool = False
    audit_required: bool = True
    custom: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentAttributes:
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: str | None = None
    geo_country: str | None = None
    geo_state: str | None = None
    geo_city: str | None = None
    network_zone: str = "public"
    user_agent: str | None = None
    request_id: str | None = None
    custom: dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    subject: SubjectAttributes
    resource: ResourceAttributes
    action: ActionAttributes
    environment: EnvironmentAttributes


@dataclass
class AccessDecision:
    effect: str  # PERMIT|DENY|NOT_APPLICABLE
    reason: str
    rule_id: str | None = None
    policy_id: str | None = None
    obligations: list[str] = field(default_factory=list)
    advice: list[str] = field(default_factory=list)
    matched_attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def is_permit(self) -> bool:
        return self.effect == "PERMIT"

    @property
    def is_deny(self) -> bool:
        return self.effect == "DENY"


@dataclass
class PolicyRule:
    rule_id: str
    description: str
    effect: PolicyEffect
    conditions: list[Callable[[AccessRequest], bool]]
    obligations: list[str] = field(default_factory=list)
    advice: list[str] = field(default_factory=list)
    priority: int = 100


@dataclass
class Policy:
    policy_id: str
    name: str
    description: str
    rules: list[PolicyRule]
    version: str = "1.0"
    is_active: bool = True


def eq(attr_path: str, value: Any) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if isinstance(value, str) and value.startswith("resource."):
            value_resolved = _resolve_path(req, value)
            return actual == value_resolved
        if isinstance(value, str) and value.startswith("subject."):
            value_resolved = _resolve_path(req, value)
            return actual == value_resolved
        return actual == value
    return check


def ne(attr_path: str, value: Any) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        return actual != value
    return check


def in_(attr_path: str, values: list[Any]) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if actual is None: return False
        return actual in values
    return check


def not_in(attr_path: str, values: list[Any]) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if actual is None: return True
        return actual not in values
    return check


def gt(attr_path: str, value: Any) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if actual is None: return False
        return operator.gt(actual, value)
    return check


def ge(attr_path: str, value: Any) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if actual is None: return False
        return operator.ge(actual, value)
    return check


def lt(attr_path: str, value: Any) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if actual is None: return False
        return operator.lt(actual, value)
    return check


def le(attr_path: str, value: Any) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if actual is None: return False
        return operator.le(actual, value)
    return check


def contains(attr_path: str, value: Any) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        target = value
        if isinstance(value, str) and (value.startswith("resource.") or value.startswith("subject.")):
            target = _resolve_path(req, value)
        if not isinstance(actual, (list, str)):
            return False
        return target in actual
    return check


def has_prefix(attr_path: str, prefix: str) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if not isinstance(actual, str): return False
        return actual.startswith(prefix)
    return check


def between(attr_path: str, low: Any, high: Any) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        actual = _resolve_path(req, attr_path)
        if actual is None: return False
        return low <= actual <= high
    return check


def and_(*conditions: Callable[[AccessRequest], bool]) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        return all(c(req) for c in conditions)
    return check


def or_(*conditions: Callable[[AccessRequest], bool]) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        return any(c(req) for c in conditions)
    return check


def not_(condition: Callable[[AccessRequest], bool]) -> Callable[[AccessRequest], bool]:
    def check(req: AccessRequest) -> bool:
        return not condition(req)
    return check


def always(req: AccessRequest) -> bool:
    return True


def never(req: AccessRequest) -> bool:
    return False


def _resolve_path(req: AccessRequest, path: str) -> Any:
    parts = path.split(".")
    if not parts: return None
    obj: Any = req
    for part in parts:
        if obj is None: return None
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            obj = getattr(obj, part, None)
    return obj


class ABACEngine:

    def __init__(self, policies: list[Policy] | None = None) -> None:
        self.policies: list[Policy] = policies or []

    def add_policy(self, policy: Policy) -> None:
        self.policies.append(policy)

    def evaluate(self, request: AccessRequest) -> AccessDecision:
        # Deny-overrides combining algorithm
        for policy in self.policies:
            if not policy.is_active: continue
            for rule in policy.rules:
                if rule.effect != PolicyEffect.DENY: continue
                if all(c(request) for c in rule.conditions):
                    return AccessDecision(
                        effect="DENY",
                        reason=rule.description,
                        rule_id=rule.rule_id,
                        policy_id=policy.policy_id,
                        obligations=rule.obligations,
                        advice=rule.advice,
                    )
        for policy in self.policies:
            if not policy.is_active: continue
            for rule in policy.rules:
                if rule.effect != PolicyEffect.PERMIT: continue
                if all(c(request) for c in rule.conditions):
                    return AccessDecision(
                        effect="PERMIT",
                        reason=rule.description,
                        rule_id=rule.rule_id,
                        policy_id=policy.policy_id,
                        obligations=rule.obligations,
                        advice=rule.advice,
                    )
        return AccessDecision(
            effect="DENY",
            reason="No policy permits this access (default deny)",
            rule_id=None,
            policy_id=None,
        )
