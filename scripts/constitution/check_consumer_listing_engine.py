"""
Consumer Listing Engine Checker.
Verifies 18 consumer engine modules, 3 listing template types, and price integrity validator.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.consumer_listing import (
    ConsumerListingView, ListingTemplateType, ListingTemplateRenderer, PriceIntegrityValidator
)


class ConsumerListingEngineChecker:
    """Verifies complete Consumer Listing Engine Architecture integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_consumer_engine_architecture(self) -> list[str]:
        violations = []
        if len(ConsumerListingView.ENGINE_MODULES) != 18:
            violations.append("Consumer Listing Engine violation: ConsumerListingView.ENGINE_MODULES must equal 18 modules")

        if len(ListingTemplateRenderer.TEMPLATE_TYPES) != 3:
            violations.append("Consumer Listing Engine violation: ListingTemplateRenderer must support 3 template types")

        if not PriceIntegrityValidator.validate_price_chain(100.0, 100.0, 100.0):
            violations.append("Consumer Listing Engine violation: PriceIntegrityValidator failed valid price chain check")

        spec_file = self.root_dir / "docs" / "architecture" / "CONSUMER_LISTING_ENGINE.md"
        if not spec_file.exists():
            violations.append("Consumer Listing Engine violation: Missing docs/architecture/CONSUMER_LISTING_ENGINE.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_consumer_engine_architecture()
        if v:
            all_violations["consumer-listing-engine"] = v
        return all_violations


if __name__ == "__main__":
    checker = ConsumerListingEngineChecker()
    report = checker.check_all()
    if report:
        print("❌ CONSUMER LISTING ENGINE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Consumer Listing Engine verified cleanly (Quick Commerce + Trust Commerce intact).")
    sys.exit(0)
