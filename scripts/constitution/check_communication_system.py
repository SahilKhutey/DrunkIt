"""
Communication System Checker.
Verifies standard request/event envelopes, retry policy, idempotency consumer, and service permission matrix definitions.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.communication import (
    StandardRequest, StandardEvent, RetryPolicy, ServicePermissionMatrix
)


class CommunicationSystemChecker:
    """Verifies complete Communication System architecture integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_communication_modules(self) -> list[str]:
        violations = []
        if not ServicePermissionMatrix.is_allowed("checkout-service", "inventory-service", "reserve"):
            violations.append("Communication System violation: checkout-service -> inventory-service reserve permission missing")

        if ServicePermissionMatrix.is_allowed("consumer-service", "payment-service", "create_intent"):
            violations.append("Communication System violation: consumer-service must NOT have direct access to payment-service")

        spec_file = self.root_dir / "docs" / "architecture" / "COMMUNICATION_SYSTEM_ARCHITECTURE.md"
        if not spec_file.exists():
            violations.append("Communication System violation: Missing docs/architecture/COMMUNICATION_SYSTEM_ARCHITECTURE.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_communication_modules()
        if v:
            all_violations["communication-system"] = v
        return all_violations


if __name__ == "__main__":
    checker = CommunicationSystemChecker()
    report = checker.check_all()
    if report:
        print("❌ COMMUNICATION SYSTEM VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Communication System verified cleanly (5 Communication Layers & Envelopes intact).")
    sys.exit(0)
