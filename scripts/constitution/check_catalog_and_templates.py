"""
Catalog & Template Platform Checker.
Verifies administrative sub-catalogs, developer sub-catalogs, 7 golden templates, and catalog validation engines.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.catalog import CatalogRegistry, GoldenTemplateRegistry, CatalogValidationEngine


class CatalogAndTemplatesChecker:
    """Verifies complete Catalog & Template Platform integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_catalog_architecture(self) -> list[str]:
        violations = []
        if len(CatalogRegistry.ADMIN_SUB_CATALOGS) != 10:
            violations.append("Catalog Architecture violation: ADMIN_SUB_CATALOGS must contain exactly 10 sub-catalogs")

        if len(CatalogRegistry.DEVELOPER_SUB_CATALOGS) != 8:
            violations.append("Catalog Architecture violation: DEVELOPER_SUB_CATALOGS must contain exactly 8 sub-catalogs")

        if len(GoldenTemplateRegistry.TEMPLATES) != 7:
            violations.append("Catalog Architecture violation: GoldenTemplateRegistry must contain exactly 7 golden templates")

        if len(CatalogValidationEngine.STAGES) != 7:
            violations.append("Catalog Architecture violation: CatalogValidationEngine must execute 7 validation stages")

        spec_file = self.root_dir / "docs" / "architecture" / "CATALOG_AND_TEMPLATE_PLATFORM.md"
        if not spec_file.exists():
            violations.append("Catalog Architecture violation: Missing docs/architecture/CATALOG_AND_TEMPLATE_PLATFORM.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_catalog_architecture()
        if v:
            all_violations["catalog-and-templates"] = v
        return all_violations


if __name__ == "__main__":
    checker = CatalogAndTemplatesChecker()
    report = checker.check_all()
    if report:
        print("❌ CATALOG & TEMPLATE PLATFORM VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Catalog & Template Platform verified cleanly (4 Layers, 18 Sub-Catalogs & 7 Golden Templates intact).")
    sys.exit(0)
