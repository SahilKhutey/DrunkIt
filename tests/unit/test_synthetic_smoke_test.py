"""
Unit tests for Synthetic Monitoring & Smoke Test engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.ops.synthetic_smoke_test import SyntheticSmokeTester


def test_synthetic_smoke_tester_report():
    tester = SyntheticSmokeTester()
    report = tester.run_full_smoke_test()

    assert report["passed"] is True
    assert report["total_probes"] == 8
    assert report["passed_probes"] == 8
    assert report["failed_probes"] == 0
    assert len(report["probes"]) == 8
