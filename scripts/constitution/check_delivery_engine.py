"""
Delivery System & Delivery Engine Checker.
Verifies 20 core modules, 14 delivery lifecycle states, 9 driver states, 7 verification states, and 14 event topics.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.delivery_engine import (
    Delivery, DeliveryStatus, DriverState, VerificationState, DeliveryEventTopics, DeliveryStateMachine
)


class DeliveryEngineChecker:
    """Verifies complete Delivery System & Delivery Engine Architecture integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_delivery_engine_architecture(self) -> list[str]:
        violations = []
        if len(Delivery.CORE_MODULES) != 20:
            violations.append("Delivery Engine violation: Delivery.CORE_MODULES must equal 20 modules")

        if len(DeliveryStatus) != 14:
            violations.append("Delivery Engine violation: DeliveryStatus must define 14 lifecycle states")

        if len(DriverState) != 9:
            violations.append("Delivery Engine violation: DriverState must define 9 driver states")

        if len(VerificationState) != 7:
            violations.append("Delivery Engine violation: VerificationState must define 7 verification states")

        if len(DeliveryEventTopics.TOPICS) != 14:
            violations.append("Delivery Engine violation: DeliveryEventTopics must define 14 event topics")

        if not DeliveryStateMachine.can_transition(DeliveryStatus.REQUESTED, DeliveryStatus.PLANNING):
            violations.append("Delivery Engine violation: DeliveryStateMachine failed valid transition check")

        spec_file = self.root_dir / "docs" / "architecture" / "DELIVERY_SYSTEM_AND_ENGINE.md"
        if not spec_file.exists():
            violations.append("Delivery Engine violation: Missing docs/architecture/DELIVERY_SYSTEM_AND_ENGINE.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_delivery_engine_architecture()
        if v:
            all_violations["delivery-engine"] = v
        return all_violations


if __name__ == "__main__":
    checker = DeliveryEngineChecker()
    report = checker.check_all()
    if report:
        print("❌ DELIVERY ENGINE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Delivery System & Delivery Engine verified cleanly (Fulfilment & Logistics Platform intact).")
    sys.exit(0)
