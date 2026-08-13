"""
Unit tests for Multi-Region Disaster Recovery verifier.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.dr.verify_dr_failover import DRFailoverVerifier


def test_dr_failover_verifier_report():
    verifier = DRFailoverVerifier(primary_region="ap-south-1", secondary_region="ap-south-2")
    report = verifier.run_full_dr_audit()

    assert report["dr_ready"] is True
    assert report["rto_target_minutes"] == 15
    assert report["rpo_target_minutes"] == 1
    assert report["database"]["status"] == "HEALTHY"
    assert report["storage"]["status"] == "ACTIVE"
