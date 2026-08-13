"""
Unit tests for Master Delivery System & Logistics Engine Architecture auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_delivery_engine import (
    DeliveryEngineChecker,
    DELIVERY_ENGINE_MAP,
)


def test_delivery_engine_spec_auditor_report():
    checker = DeliveryEngineChecker(root_dir=root_dir)
    res = checker.audit_delivery_engine()

    assert res["total_modules"] == 15
    assert res["verified_modules"] == 15
    assert res["score_pct"] == 100.0
    assert len(DELIVERY_ENGINE_MAP) == 15

    # Test key modules across 10 Delivery Roadmap Phases, State Machine, Dispatch Scoring, POD, and Returns
    assert DELIVERY_ENGINE_MAP["DEL-PH-01"] == "D1 - Delivery Domain Models (Delivery, DeliveryJob, DriverAssignment)"
    assert DELIVERY_ENGINE_MAP["DEL-PH-03"] == "D3 - Dispatch Engine (Driver candidate filtering, Assignment scoring)"
    assert DELIVERY_ENGINE_MAP["DEL-PH-05"] == "D5 - Real-Time Tracking Engine (GPS, Redis Streams, WebSocket Gateway)"
    assert DELIVERY_ENGINE_MAP["DEL-PH-07"] == "D7 - Verification & Handoff (Age check, OTP/QR token, POD object)"
    assert DELIVERY_ENGINE_MAP["DEL-STA-01"] == "10-Stage Delivery State Machine"
    assert DELIVERY_ENGINE_MAP["DEL-ALG-01"] == "Deterministic Driver Dispatch Scoring Formula"
    assert DELIVERY_ENGINE_MAP["DEL-POD-01"] == "Proof of Delivery (POD) & Verification Evidence Isolation"
    assert DELIVERY_ENGINE_MAP["DEL-RET-01"] == "Controlled Handoff Return Engine (DRIVER_RETURN -> STORE_RECEIPT)"
