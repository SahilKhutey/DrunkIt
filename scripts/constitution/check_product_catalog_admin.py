"""
Product Catalog Admin Checker.
Verifies 10-step wizard, 12 template field types, and Admin vs Retailer permission matrix.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.product_admin import (
    ProductWizardEngine, FieldType, AdminRetailerPermissionsMatrix, PermissionAction
)


class ProductCatalogAdminChecker:
    """Verifies complete Product Catalog Admin System Architecture integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_admin_architecture(self) -> list[str]:
        violations = []
        if len(ProductWizardEngine.STEPS_ORDER) != 10:
            violations.append("Product Catalog Admin violation: ProductWizardEngine must define exactly 10 wizard steps")

        if len(FieldType) != 12:
            violations.append("Product Catalog Admin violation: FieldType must define exactly 12 template field types")

        if not AdminRetailerPermissionsMatrix.can_admin(PermissionAction.SUSPEND_PRODUCT_GLOBALLY):
            violations.append("Product Catalog Admin violation: Admin must have SUSPEND_PRODUCT_GLOBALLY permission")

        if AdminRetailerPermissionsMatrix.can_retailer(PermissionAction.SUSPEND_PRODUCT_GLOBALLY):
            violations.append("Product Catalog Admin violation: Retailer must NOT have SUSPEND_PRODUCT_GLOBALLY permission")

        spec_file = self.root_dir / "docs" / "architecture" / "PRODUCT_CATALOG_ADMIN_SYSTEM.md"
        if not spec_file.exists():
            violations.append("Product Catalog Admin violation: Missing docs/architecture/PRODUCT_CATALOG_ADMIN_SYSTEM.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_admin_architecture()
        if v:
            all_violations["product-catalog-admin"] = v
        return all_violations


if __name__ == "__main__":
    checker = ProductCatalogAdminChecker()
    report = checker.check_all()
    if report:
        print("❌ PRODUCT CATALOG ADMIN VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Product Catalog Admin System verified cleanly (10-Step Wizard & Admin/Retailer Matrix intact).")
    sys.exit(0)
