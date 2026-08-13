"""
Unit tests for Platform Health & Diagnostic CLI tool.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.ops.platform_health_check import PlatformHealthChecker, SERVICE_PORT_MAP


def test_platform_health_checker_report():
    checker = PlatformHealthChecker()
    report = checker.generate_report()

    assert report["total_services"] == 17
    assert report["healthy_services"] == 17
    assert report["system_health_pct"] == 100.0
    assert len(SERVICE_PORT_MAP) == 17
    assert SERVICE_PORT_MAP["gateway"] == 8000
    assert SERVICE_PORT_MAP["support-agent"] == 8016
