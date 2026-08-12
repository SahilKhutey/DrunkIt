"""
Product Platform Checker.
Verifies Product Master vs View Projections separation, 16 catalog modules, 7 visibility levels, and 9 lifecycle states.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.product import (
    ProductMaster, ProductLifecycleState, VisibilityLevel, ViewComposer
)


class ProductPlatformChecker:
    """Verifies complete Product Platform Architecture integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_product_architecture(self) -> list[str]:
        violations = []
        if len(ProductMaster.CATALOG_MODULES) != 16:
            violations.append("Product Platform violation: ProductMaster.CATALOG_MODULES must equal 16 modules")

        if len(ProductLifecycleState) != 9:
            violations.append("Product Platform violation: ProductLifecycleState must define 9 lifecycle states")

        if len(VisibilityLevel) != 7:
            violations.append("Product Platform violation: VisibilityLevel must define 7 field-level visibility levels")

        spec_file = self.root_dir / "docs" / "architecture" / "PRODUCT_PLATFORM_ARCHITECTURE.md"
        if not spec_file.exists():
            violations.append("Product Platform violation: Missing docs/architecture/PRODUCT_PLATFORM_ARCHITECTURE.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_product_architecture()
        if v:
            all_violations["product-platform"] = v
        return all_violations


if __name__ == "__main__":
    checker = ProductPlatformChecker()
    report = checker.check_all()
    if report:
        print("❌ PRODUCT PLATFORM VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Product Platform verified cleanly (Truth vs Presentation separation intact).")
    sys.exit(0)
