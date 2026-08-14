"""Immutable Security Principal object holding authenticated user identity and capabilities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    """Represents an authenticated user principal with assigned roles and permissions."""

    user_id: uuid.UUID
    roles: frozenset[str]
    permissions: frozenset[str]
    tenant_id: str | None = None

    def has_role(self, role: str) -> bool:
        """Check if principal possesses specified role."""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Check if principal possesses specified permission."""
        return permission in self.permissions
