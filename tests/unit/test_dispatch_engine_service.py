"""
Unit tests for Master Phase D3 Dispatch Engine Service auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_dispatch_engine_service import (
    DispatchEngineServiceChecker,
    DISPATCH_ENGINE_MAP,
)


def test_dispatch_engine_service_auditor_report():
    checker = DispatchEngineServiceChecker(root_dir=root_dir)
    res = checker.audit_dispatch_engine_service()

    assert res["total_modules"] == 10
    assert res["verified_modules"] == 10
    assert res["score_pct"] == 100.0
    assert len(DISPATCH_ENGINE_MAP) == 10

    # Test key modules
    assert DISPATCH_ENGINE_MAP["DSP-D3-01"] == "Haversine Distance Engine (haversine_distance_km)"
    assert DISPATCH_ENGINE_MAP["DSP-D3-02"] == "Pickup ETA Estimation Engine (estimate_pickup_minutes)"
    assert DISPATCH_ENGINE_MAP["DSP-D3-03"] == "Deterministic Candidate Scoring Engine (calculate_driver_score)"
    assert DISPATCH_ENGINE_MAP["DSP-D3-05"] == "Driver Service Client (get_available_drivers, reserve_driver)"
    assert DISPATCH_ENGINE_MAP["DSP-D3-06"] == "Delivery Service Client (move_to_dispatching, assign_driver, move_to_assigned)"
    assert DISPATCH_ENGINE_MAP["DSP-D3-08"] == "Atomic Driver Reservation (UPDATE drivers SET operational_status='RESERVED')"
    assert DISPATCH_ENGINE_MAP["DSP-D3-10"] == "Service Isolation Rule (No direct DB access across service boundaries)"
