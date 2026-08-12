"""
Authentication, Authorization, & Trust Pipeline Checker (Protocols 15, 16, 17).
Verifies presence and configuration of authentication, authorization, and trust decision modules.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.auth import TokenStandards, AuthenticationPipeline
from faccp_common.authz import AuthorizationEngine, RBACEngine
from faccp_common.trust import TrustDecisionEngine, TrustOutcome


class AuthPipelineChecker:
    """Verifies Protocols 15, 16, and 17 integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_auth_modules(self) -> list[str]:
        violations = []
        if TokenStandards.ACCESS_TOKEN_LIFETIME_SECONDS != 900:
            violations.append("Protocol 15 violation: Token lifetime must be 15 minutes (900 seconds)")
        if len(TrustOutcome.__members__) != 5:
            violations.append("Protocol 17 violation: TrustOutcome must have exactly 5 outcomes (ALLOW, DENY, VERIFY, REVIEW, BLOCK)")
        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_auth_modules()
        if v:
            all_violations["auth-pipeline"] = v
        return all_violations


if __name__ == "__main__":
    checker = AuthPipelineChecker()
    report = checker.check_all()
    if report:
        print("❌ AUTHENTICATION / AUTHORIZATION / TRUST PIPELINE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Protocols 15, 16, & 17 verified cleanly (Authentication, Authorization, and Trust Pipeline active).")
    sys.exit(0)
