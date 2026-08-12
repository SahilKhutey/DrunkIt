"""
RBAC Engine (§16.1).
"""

from __future__ import annotations

from dataclasses import dataclass
from ..roles import Role, ROLE_PERMISSIONS


@dataclass
class RBACDecision:
    allowed: bool
    matched_role: str | None = None
    reason: str | None = None
    required_permission: str | None = None


class RBACEngine:
    def __init__(self) -> None:
        self.role_permissions = ROLE_PERMISSIONS

    def check(self, user_roles: list[str], required_permission: str) -> RBACDecision:
        if "SUPER_ADMIN" in user_roles or "PLATFORM_ROOT" in user_roles:
            return RBACDecision(allowed=True, matched_role="SUPER_ADMIN", reason="super_admin")

        all_permissions: set[str] = set()
        for r_str in user_roles:
            try:
                role_enum = Role(r_str)
                perms = self.role_permissions.get(role_enum, frozenset())
                for p in perms:
                    p_val = p.value if hasattr(p, "value") else str(p)
                    all_permissions.add(p_val)
                    if ":" in p_val:
                        all_permissions.add(f"{p_val.split(':')[0]}:*")
            except ValueError:
                pass

        if required_permission in all_permissions:
            return RBACDecision(allowed=True, matched_role=user_roles[0] if user_roles else None)

        if ":" in required_permission:
            domain = required_permission.split(":")[0]
            if f"{domain}:*" in all_permissions:
                return RBACDecision(allowed=True, matched_role=user_roles[0] if user_roles else None, reason="wildcard")

        return RBACDecision(
            allowed=False,
            reason=f"None of {user_roles} grants '{required_permission}'",
            required_permission=required_permission,
        )
