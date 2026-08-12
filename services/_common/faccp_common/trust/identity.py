"""Identity model — every actor on the platform."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ActorType(str, Enum):
    """All actor types on the platform."""

    CONSUMER = "CONSUMER"
    RETAILER_OWNER = "RETAILER_OWNER"
    RETAILER_STAFF = "RETAILER_STAFF"
    DRIVER = "DRIVER"
    ADMIN = "ADMIN"
    EMPLOYEE = "EMPLOYEE"
    AUDITOR = "AUDITOR"
    SERVICE = "SERVICE"
    API_CONSUMER = "API_CONSUMER"
    DEVICE = "DEVICE"
    SYSTEM = "SYSTEM"


@dataclass
class Identity:
    """A platform identity (human or non-human)."""

    actor_id: str
    actor_type: ActorType
    primary_identifier: str
    display_name: str
    roles: list[str] = field(default_factory=list)
    status: str = "active"
    mfa_enabled: bool = False
    trust_score: int = 50
    risk_score: int = 0
    organization_id: str | None = None
    assigned_stores: list[str] = field(default_factory=list)
    assigned_jurisdictions: list[str] = field(default_factory=list)
    consumer_level: str | None = None
    seller_level: str | None = None
    tenant_id: str | None = None
    device_id: str | None = None
    session_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def new_id() -> str:
        return f"usr_{uuid.uuid4().hex}"

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, roles: list[str]) -> bool:
        return any(r in self.roles for r in roles)

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "actor_type": self.actor_type.value,
            "primary_identifier": self.primary_identifier,
            "display_name": self.display_name,
            "roles": self.roles,
            "status": self.status,
            "mfa_enabled": self.mfa_enabled,
            "trust_score": self.trust_score,
            "risk_score": self.risk_score,
            "organization_id": self.organization_id,
            "assigned_stores": self.assigned_stores,
            "assigned_jurisdictions": self.assigned_jurisdictions,
            "consumer_level": self.consumer_level,
            "seller_level": self.seller_level,
            "tenant_id": self.tenant_id,
            "device_id": self.device_id,
            "session_id": self.session_id,
        }


@dataclass
class AuthenticatedContext:
    """Context built after successful authentication, propagated through request."""

    identity: Identity
    claims: dict[str, Any]
    session_expires_at: datetime | None = None
    mfa_verified: bool = False
    mfa_timestamp: datetime | None = None
    device_trust_score: int = 50

    def is_mfa_fresh(self, max_age_seconds: int = 900) -> bool:
        if not self.mfa_verified or not self.mfa_timestamp:
            return False
        age = (datetime.now(timezone.utc) - self.mfa_timestamp).total_seconds()
        return age <= max_age_seconds

    def to_abac_subject(self):
        from faccp_common.trust.authorization import SubjectAttributes
        return SubjectAttributes(
            user_id=self.identity.actor_id,
            primary_role=self.identity.roles[0] if self.identity.roles else "CONSUMER",
            roles=self.identity.roles,
            organization_id=self.identity.organization_id,
            assigned_stores=self.identity.assigned_stores,
            assigned_jurisdictions=self.identity.assigned_jurisdictions,
            mfa_enabled=self.identity.mfa_enabled,
            mfa_verified=self.mfa_verified,
            trust_score=self.identity.trust_score,
            risk_score=self.identity.risk_score,
            is_active=self.identity.status == "active",
        )
