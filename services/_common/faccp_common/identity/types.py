"""
Actor Types & Fundamental Identity (§14.1).
"""

from __future__ import annotations

from enum import Enum


class ActorType(str, Enum):
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


class Identity:
    """The fundamental platform identity."""

    def __init__(
        self,
        actor_id: str,
        actor_type: ActorType,
        primary_identifier: str,
        display_name: str,
        roles: list[str] | None = None,
        status: str = "active",
        mfa_enabled: bool = False,
        trust_score: int = 50,
    ) -> None:
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.primary_identifier = primary_identifier
        self.display_name = display_name
        self.roles = roles or []
        self.status = status
        self.mfa_enabled = mfa_enabled
        self.trust_score = trust_score
