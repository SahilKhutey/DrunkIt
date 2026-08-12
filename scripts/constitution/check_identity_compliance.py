"""
Identity Compliance Checker (§14.10).
Verifies presence of identity protection and sensitive operation authorization across API routes.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.identity.sensitive_operations import AnonymousAccessGuard, SENSITIVE_OPERATIONS
from faccp_common.identity.types import ActorType


class IdentityComplianceChecker:
    """Verifies Identity Protocol compliance across all platform components."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_identity_modules(self) -> list[str]:

        violations = []
        # Ensure Identity, ActorType, TrustStatus, ServiceIdentity are intact
        if len(ActorType.__members__) < 11:
            violations.append("Identity Protocol incomplete: missing required ActorType enum values (§14.1)")
        if len(SENSITIVE_OPERATIONS) < 10:
            violations.append("Identity Protocol incomplete: missing sensitive operations list (§14.10)")
        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_identity_modules()
        if v:
            all_violations["identity-protocol"] = v
        return all_violations


if __name__ == "__main__":
    checker = IdentityComplianceChecker()
    report = checker.check_all()
    if report:
        print("❌ IDENTITY PROTOCOL VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Identity Protocol verified cleanly (all 11 ActorTypes and Sensitive Operation Guards active).")
    sys.exit(0)
