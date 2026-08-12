"""
Web UI Platform Checker.
Verifies 4 Role-Aware Portals, 6 UI principles, 9 token categories, 7 status visual treatments, and WCAG accessibility standards.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.ui import (
    PortalRegistry, DesignTokens, AccessibilityGuidelines, WCAGLevel
)


class WebUIPlatformChecker:
    """Verifies complete Web UI & Visual Development Architecture integrity."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_ui_architecture(self) -> list[str]:
        violations = []
        if len(PortalRegistry.PORTALS) != 4:
            violations.append("Web UI Architecture violation: PortalRegistry must define exactly 4 portals")

        if len(PortalRegistry.PRINCIPLES) != 6:
            violations.append("Web UI Architecture violation: PortalRegistry must enforce 6 UI architecture principles")

        if len(PortalRegistry.STATUS_TREATMENTS) != 7:
            violations.append("Web UI Architecture violation: PortalRegistry must define 7 status visual treatments")

        if len(DesignTokens.CATEGORIES) != 9:
            violations.append("Web UI Architecture violation: DesignTokens must define 9 token categories")

        if AccessibilityGuidelines.TARGET_LEVEL != WCAGLevel.AA:
            violations.append("Web UI Architecture violation: Accessibility target level must be WCAG 2.2 AA")

        spec_file = self.root_dir / "docs" / "architecture" / "WEB_UI_VISUAL_DEVELOPMENT_GUIDE.md"
        if not spec_file.exists():
            violations.append("Web UI Architecture violation: Missing docs/architecture/WEB_UI_VISUAL_DEVELOPMENT_GUIDE.md")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_ui_architecture()
        if v:
            all_violations["web-ui-platform"] = v
        return all_violations


if __name__ == "__main__":
    checker = WebUIPlatformChecker()
    report = checker.check_all()
    if report:
        print("❌ WEB UI PLATFORM VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Web UI Platform verified cleanly (4 Role-Aware Portals & Design Tokens intact).")
    sys.exit(0)
