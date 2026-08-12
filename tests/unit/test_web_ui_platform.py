"""
Unit tests for Web UI Platform Architecture (4 Portals, 6 Principles, Design Tokens, Accessibility).
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from faccp_common.ui import (
    PortalRegistry, PortalType, DesignTokens, AccessibilityGuidelines, WCAGLevel
)
from scripts.constitution.check_web_ui_platform import WebUIPlatformChecker


def test_portal_registry_definitions():
    assert len(PortalRegistry.PORTALS) == 4
    consumer_portal = PortalRegistry.PORTALS[PortalType.CONSUMER]
    assert consumer_portal.name == "Consumer Portal"
    assert len(PortalRegistry.PRINCIPLES) == 6
    assert len(PortalRegistry.STATUS_TREATMENTS) == 7


def test_design_tokens_categories():
    assert len(DesignTokens.CATEGORIES) == 9
    assert len(DesignTokens.COMPONENT_LAYERS) == 7


def test_accessibility_guidelines():
    assert AccessibilityGuidelines.TARGET_LEVEL == WCAGLevel.AA
    assert len(AccessibilityGuidelines.REQUIREMENTS) == 8


def test_web_ui_platform_checker():
    checker = WebUIPlatformChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
