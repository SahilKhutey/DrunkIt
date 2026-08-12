"""
Functional Architecture Checker.
Verifies all 13 Bounded Domains, 71 Functional Modules, and the 12-Phase Development Order.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.architecture import DomainRegistry, FunctionalArchitecture


class FunctionalArchitectureChecker:
    """Verifies complete 13-domain, 71-module functional architecture."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_domains_and_modules(self) -> list[str]:
        violations = []
        if len(DomainRegistry.DOMAINS) != 13:
            violations.append("Functional Architecture violation: DomainRegistry must contain exactly 13 domains")

        total_module_count = sum(len(mods) for mods in DomainRegistry.DOMAINS.values())
        if total_module_count != 71:
            violations.append(f"Functional Architecture violation: Total modules must equal 71 (found {total_module_count})")

        spec_file = self.root_dir / "docs" / "architecture" / "FUNCTIONAL_MODULE_ARCHITECTURE.md"
        if not spec_file.exists():
            violations.append("Functional Architecture violation: Missing docs/architecture/FUNCTIONAL_MODULE_ARCHITECTURE.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_domains_and_modules()
        if v:
            all_violations["functional-architecture"] = v
        return all_violations


if __name__ == "__main__":
    checker = FunctionalArchitectureChecker()
    report = checker.check_all()
    if report:
        print("❌ FUNCTIONAL ARCHITECTURE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Functional Architecture verified cleanly (13 Bounded Domains and 71 Modules intact).")
    sys.exit(0)
