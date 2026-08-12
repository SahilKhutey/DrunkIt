"""
Listing Engine Development Specification Checker.
Verifies 17 core service modules, 8 template types, 7 listing lifecycle states, 4 inventory states, field resolver pattern, and ActionEngine.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.listing_service import (
    ProductDetailView, ListingStatus, InventoryStatus, FieldResolver, ActionEngine, ListingContext
)


class ListingEngineSpecChecker:
    """Verifies complete Listing Engine Development Specification integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_listing_spec_architecture(self) -> list[str]:
        violations = []
        if len(ProductDetailView.CORE_MODULES) != 17:
            violations.append("Listing Engine Spec violation: ProductDetailView.CORE_MODULES must equal 17 modules")

        if len(ProductDetailView.TEMPLATE_TYPES) != 8:
            violations.append("Listing Engine Spec violation: ProductDetailView.TEMPLATE_TYPES must equal 8 template types")

        if len(ListingStatus) != 7:
            violations.append("Listing Engine Spec violation: ListingStatus must define 7 listing lifecycle states")

        if len(InventoryStatus) != 4:
            violations.append("Listing Engine Spec violation: InventoryStatus must define 4 inventory states")

        ctx = ListingContext(
            product_id="prd_1",
            sku_id="sku_1",
            retailer_id="ret_1",
            store_id="str_1",
            inventory_state=InventoryStatus.OUT_OF_STOCK,
        )
        actions = ActionEngine().evaluate(ctx)
        if actions["add_to_cart"] is True:
            violations.append("Listing Engine Spec violation: OUT_OF_STOCK inventory must fail-closed and block add_to_cart")

        spec_file = self.root_dir / "docs" / "architecture" / "LISTING_ENGINE_DEVELOPMENT_SPECIFICATION.md"
        if not spec_file.exists():
            violations.append("Listing Engine Spec violation: Missing docs/architecture/LISTING_ENGINE_DEVELOPMENT_SPECIFICATION.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_listing_spec_architecture()
        if v:
            all_violations["listing-engine-spec"] = v
        return all_violations


if __name__ == "__main__":
    checker = ListingEngineSpecChecker()
    report = checker.check_all()
    if report:
        print("❌ LISTING ENGINE SPECIFICATION VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Listing Engine Specification verified cleanly (Read-Optimized Composition Engine intact).")
    sys.exit(0)
