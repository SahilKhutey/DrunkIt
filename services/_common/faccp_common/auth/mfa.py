"""
MFA Enforcement Rules (§15.5).
"""

from __future__ import annotations


class MFAEnforcement:
    MFA_REQUIRED_ROLES: frozenset[str] = frozenset({
        "SUPER_ADMIN", "REGULATORY_ADMIN", "STATE_ADMIN", "DISTRICT_ADMIN",
        "SECURITY_ADMIN", "DATA_PROTECTION_OFFICER", "FINANCE_ADMIN",
        "RETAILER_OWNER", "STORE_MANAGER", "DELIVERY_AGENT",
        "AUDITOR", "INTERNAL_AUDITOR", "COMPLIANCE_OFFICER",
    })

    MFA_REQUIRED_ACTIONS: frozenset[str] = frozenset({
        "user:create", "user:delete", "user:lock", "user:unlock",
        "role:assign", "role:revoke", "permission:grant",
        "license:approve", "license:revoke", "license:suspend",
        "policy:activate", "policy:rollback",
        "payment:refund", "refund:approve", "settlement:approve",
        "verification:approve", "verification:reject",
        "data:export", "data:delete", "audit:export",
    })

    FRESH_MFA_ACTIONS: frozenset[str] = frozenset({
        "user:lock", "user:unlock", "role:assign", "role:revoke",
        "license:revoke", "policy:rollback", "settlement:execute",
        "data:delete", "mfa:disable",
    })

    FRESH_MFA_WINDOW_SECONDS = 900  # 15 minutes

    @classmethod
    def requires_mfa(cls, role: str, action: str) -> bool:
        return role in cls.MFA_REQUIRED_ROLES or action in cls.MFA_REQUIRED_ACTIONS

    @classmethod
    def requires_fresh_mfa(cls, role: str, action: str) -> bool:
        return action in cls.FRESH_MFA_ACTIONS
