"""
Unit tests for Master Web UI & Visual Development Architecture auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_web_ui_architecture import (
    WebUIArchitectureChecker,
    WEB_UI_ARCHITECTURE_MAP,
)


def test_web_ui_architecture_auditor_report():
    checker = WebUIArchitectureChecker(root_dir=root_dir)
    res = checker.audit_web_ui_architecture()

    assert res["total_modules"] == 23
    assert res["verified_modules"] == 23
    assert res["score_pct"] == 100.0
    assert len(WEB_UI_ARCHITECTURE_MAP) == 23

    # Test key modules across Principles, Portals, Tokens, Primitives, State, Accessibility, and Errors
    assert WEB_UI_ARCHITECTURE_MAP["UI-PRN-01"] == "Principle P1 - Role Separation Across Portals"
    assert WEB_UI_ARCHITECTURE_MAP["UI-PORT-01"] == "Consumer Web Portal Architecture (apps/consumer-web/)"
    assert WEB_UI_ARCHITECTURE_MAP["UI-PORT-02"] == "Retailer Web Portal Architecture (apps/retailer-web/)"
    assert WEB_UI_ARCHITECTURE_MAP["UI-PORT-03"] == "Admin Web Portal Architecture (apps/admin-web/)"
    assert WEB_UI_ARCHITECTURE_MAP["UI-PORT-04"] == "Driver Mobile Application Architecture (apps/driver-app/)"
    assert WEB_UI_ARCHITECTURE_MAP["UI-TOK-01"] == "Design Token Registry (Colors, Typography, Spacing 4-80px, Radius, Shadows, Motion)"
    assert WEB_UI_ARCHITECTURE_MAP["UI-CMP-01"] == "UI Primitives Layer (Button, Input, Badge, Icon, Tooltip, Avatar, Spinner)"
    assert WEB_UI_ARCHITECTURE_MAP["UI-STA-03"] == "Server State Integration (TanStack Query / API Client)"
    assert WEB_UI_ARCHITECTURE_MAP["UI-ACC-01"] == "WCAG 2.2 AA Accessibility Controls (Keyboard Focus, ARIA, High Contrast, Reduced Motion)"
