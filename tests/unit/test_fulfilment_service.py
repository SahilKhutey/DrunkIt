"""
Unit tests for Master Phase D4 Fulfilment + Serviceability Engine Service auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_fulfilment_service import (
    FulfilmentServiceChecker,
    FULFILMENT_SERVICE_MAP,
)


def test_fulfilment_service_auditor_report():
    checker = FulfilmentServiceChecker(root_dir=root_dir)
    res = checker.audit_fulfilment_service()

    assert res["total_modules"] == 10
    assert res["verified_modules"] == 10
    assert res["score_pct"] == 100.0
    assert len(FULFILMENT_SERVICE_MAP) == 10

    # Test key modules
    assert FULFILMENT_SERVICE_MAP["FLF-D4-01"] == "Geospatial Haversine Distance Engine (distance_km)"
    assert FULFILMENT_SERVICE_MAP["FLF-D4-03"] == "Machine-Readable Serviceability Codes (ServiceabilityReason)"
    assert FULFILMENT_SERVICE_MAP["FLF-D4-05"] == "Inventory Item Schema & Sellable Quantity Logic (InventoryItem, InventoryReservation)"
    assert FULFILMENT_SERVICE_MAP["FLF-D4-07"] == "Store Selection Scoring Engine (calculate_store_score combining distance 45%, inventory 35%, capacity 20%)"
    assert FULFILMENT_SERVICE_MAP["FLF-D4-08"] == "Alcohol-Specific Compliance Decision Gate (ComplianceDecision)"
    assert FULFILMENT_SERVICE_MAP["FLF-D4-09"] == "Fulfilment Planner & Deterministic Fulfilment Plan Object (FulfilmentPlanner, FulfilmentPlan)"
    assert FULFILMENT_SERVICE_MAP["FLF-D4-10"] == "FastAPI Application Entry Point & Port Topology (:8003)"
