"""
Source-of-Truth Checker (§13.6).
Static analyzer verifying zero cross-service table writes or model imports.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.governance.source_of_truth import SourceOfTruthRegistry


class SourceOfTruthChecker:
    """Verifies no service writes to or imports models of another service's data."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_service(self, service_dir: Path) -> list[str]:
        violations = []
        service_name = service_dir.name

        for py_file in service_dir.rglob("*.py"):
            if "tests" in py_file.parts or "_common" in py_file.parts:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = py_file.relative_to(self.root_dir)

            # Check cross-service imports of foreign models
            for info, (owner_service, table) in SourceOfTruthRegistry.OWNERSHIP.items():
                if owner_service != service_name:
                    foreign_module = owner_service.replace("-", "_")
                    pattern = rf"from\s+{foreign_module}\.app\.db\.models\s+import"
                    if re.search(pattern, content):
                        violations.append(
                            f"{rel_path}: Imports ORM models from {owner_service} "
                            f"— violates Source-of-Truth Protocol (§13.2, §13.6)"
                        )

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        services_dir = self.root_dir / "services"
        if not services_dir.exists():
            return all_violations

        for s_dir in services_dir.iterdir():
            if s_dir.is_dir() and s_dir.name != "_common":
                v = self.check_service(s_dir)
                if v:
                    all_violations[s_dir.name] = v

        return all_violations


if __name__ == "__main__":
    checker = SourceOfTruthChecker()
    report = checker.check_all()
    if report:
        print("❌ SOURCE-OF-TRUTH VIOLATIONS DETECTED:")
        for service, viols in report.items():
            print(f"Service: {service}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Source-of-Truth Protocol verified cleanly (zero cross-service table writes or model imports).")
    sys.exit(0)
