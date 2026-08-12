"""
Security Standards as codified in Article 1 of the System Constitution (§1.1).
"""

from __future__ import annotations


class SecurityStandard:
    PUBLIC_ROUTES_ALLOWLIST: frozenset[str] = frozenset({
        "/health",
        "/ready",
        "/metrics",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/password/reset/request",
        "/api/v1/auth/refresh",
        "/api/v1/webhooks/{provider}",  # signature-verified
    })

    @staticmethod
    def requires_mfa(role: str, action: str) -> bool:
        """Determines if an action or role requires MFA verification."""
        role_upper = role.upper()
        high_risk_roles = {"SUPER", "SECURITY", "DPO", "ADMIN"}
        sensitive_actions = {"approve", "verify", "suspend", "revoke", "export", "delete_account"}
        
        return any([
            any(r in role_upper for r in high_risk_roles),
            action.lower() in sensitive_actions,
        ])

    @staticmethod
    def mfa_max_age_seconds() -> int:
        """Maximum age for MFA authorization claim in seconds (15 mins)."""
        return 900
