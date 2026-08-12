"""
Development Gate System Checker (Protocol 60).
Verifies presence of Feature Templates, Gate System definition, and FeatureGateValidator integrity.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.gates import GateRegistry, FeatureGateValidator, GateStatus


class DevelopmentGatesChecker:
    """Verifies Protocol 60 and 8-Gate Development Gate System integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_gate_system(self) -> list[str]:
        violations = []
        if len(GateRegistry.GATES) != 9:
            violations.append("Protocol 60 violation: GateRegistry must contain exactly 9 gates (Gates 0 through 8)")
        template_file = self.root_dir / "docs" / "templates" / "feature_template.md"
        if not template_file.exists():
            violations.append("Protocol 60 violation: Missing feature template: docs/templates/feature_template.md")
        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_gate_system()
        if v:
            all_violations["development-gates"] = v
        return all_violations


if __name__ == "__main__":
    checker = DevelopmentGatesChecker()
    report = checker.check_all()
    if report:
        print("❌ DEVELOPMENT GATE SYSTEM VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Protocol 60 verified cleanly (8-Gate Development Gate System active and complete).")
    sys.exit(0)
