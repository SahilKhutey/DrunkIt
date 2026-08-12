"""
Anonymous Access Guard & Sensitive Operations Mandate (§14.10).
"""

from __future__ import annotations

from typing import Any
from ..exceptions import ForbiddenError, UnauthorizedError
from .types import Identity

SENSITIVE_OPERATIONS: frozenset[str] = frozenset({
    # Commerce
    "order:create",
    "payment:create",
    "payment:refund",
    "cart:checkout",

    # Compliance
    "license:approve",
    "license:revoke",
    "policy:activate",
    "policy:rollback",

    # Admin
    "admin:privilege_change",
    "admin:user_lock",
    "admin:user_unlock",
    "admin:data_export",
    "admin:audit_export",

    # Verification
    "verification:approve",
    "verification:reject",

    # Security & Financial
    "security:incident_respond",
    "security:key_rotate",
    "settlement:approve",
    "settlement:execute",
    "refund:override",
})


class AnonymousAccessGuard:
    """Ensures no anonymous access to sensitive operations."""

    @staticmethod
    def require_authenticated(actor: Identity | None, action: str) -> None:
        if action in SENSITIVE_OPERATIONS:
            if actor is None:
                raise UnauthorizedError(
                    f"Authentication required for sensitive operation: {action}",
                    details={"action": action, "code": "ANONYMOUS_ACCESS_DENIED"},
                )
            if actor.status != "active":
                raise ForbiddenError(
                    f"Account not active: {actor.status}",
                    details={"action": action, "actor_status": actor.status},
                )
