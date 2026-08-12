"""
Authentication Pipeline & Authenticated Context (§15.3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from ..identity.types import ActorType, Identity
from .tokens import validate_access_token


@dataclass
class AuthenticatedContext:
    user_id: str
    claims: dict[str, Any]
    roles: list[str] = field(default_factory=list)
    primary_role: str = "CONSUMER"
    permissions: list[str] = field(default_factory=list)
    organization_id: str | None = None
    assigned_stores: list[str] = field(default_factory=list)
    assigned_jurisdictions: list[str] = field(default_factory=list)
    consumer_level: str | None = None
    seller_level: str | None = None
    mfa_verified: bool = False
    trust_score: int = 50
    device_id: str | None = None
    session_id: str | None = None

    @classmethod
    def from_claims(cls, claims: dict[str, Any]) -> AuthenticatedContext:
        user_id = claims["sub"]
        roles = claims.get("roles", [])
        primary_role = claims.get("primary_role") or (roles[0] if roles else "CONSUMER")
        return cls(
            user_id=user_id,
            claims=claims,
            roles=roles,
            primary_role=primary_role,
            permissions=claims.get("permissions", []),
            organization_id=claims.get("organization_id"),
            assigned_stores=claims.get("assigned_stores", []),
            assigned_jurisdictions=claims.get("assigned_jurisdictions", []),
            consumer_level=claims.get("consumer_level"),
            seller_level=claims.get("seller_level"),
            mfa_verified=claims.get("mfa_verified", False),
            trust_score=claims.get("trust_score", 50),
            device_id=claims.get("device_id"),
            session_id=claims.get("session_id"),
        )

    @property
    def identity(self) -> Identity:
        return Identity(
            actor_id=self.user_id,
            actor_type=ActorType.CONSUMER if "CONSUMER" in self.roles else ActorType.ADMIN,
            primary_identifier=self.claims.get("email", self.user_id),
            display_name=self.claims.get("display_name", self.user_id[:8]),
            roles=self.roles,
            mfa_enabled=self.mfa_verified,
            trust_score=self.trust_score,
        )

    def to_abac_subject(self) -> Any:
        from ..abac.engine import SubjectAttributes
        return SubjectAttributes(
            user_id=self.user_id,
            roles=self.roles,
            primary_role=self.primary_role,
            permissions=self.permissions,
            organization_id=self.organization_id,
            assigned_stores=self.assigned_stores,
            assigned_jurisdictions=self.assigned_jurisdictions,
            consumer_level=self.consumer_level,
            seller_level=self.seller_level,
            mfa_verified=self.mfa_verified,
            trust_score=self.trust_score,
        )


class AuthenticationPipeline:
    """Standard authentication pipeline validator."""

    def authenticate_token(self, token: str, secret_key: str | None = None) -> AuthenticatedContext:
        claims = validate_access_token(token, secret_key=secret_key)
        return AuthenticatedContext.from_claims(claims)
