"""
Unit tests for Delivery System & Delivery Engine Architecture (Fulfilment & Logistics Platform, 20 Modules, 14 Delivery States, 9 Driver States, Dispatch Engine).
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

from faccp_common.delivery_engine import (
    DeliveryStatus, DriverState, VerificationState, DeliveryStateMachine,
    Delivery, Location, CandidateDriver, DispatchEngine, DriverScorer, DeliveryEventPublisher
)
from scripts.constitution.check_delivery_engine import DeliveryEngineChecker


def test_delivery_state_machine_valid_transitions():
    assert len(Delivery.CORE_MODULES) == 20
    assert len(DeliveryStatus) == 14
    assert len(DriverState) == 9
    assert len(VerificationState) == 7

    assert DeliveryStateMachine.can_transition(DeliveryStatus.REQUESTED, DeliveryStatus.PLANNING) is True
    assert DeliveryStateMachine.can_transition(DeliveryStatus.REQUESTED, DeliveryStatus.DELIVERED) is False


def test_dispatch_engine_scoring():
    d1 = CandidateDriver(driver_id="drv_1", distance_km=1.2, eta_minutes=10.0, reliability_score=0.98, is_available=True)
    d2 = CandidateDriver(driver_id="drv_2", distance_km=4.5, eta_minutes=25.0, reliability_score=0.85, is_available=True)

    scorer1 = DriverScorer.score_driver(d1)
    scorer2 = DriverScorer.score_driver(d2)

    assert scorer1 > scorer2

    engine = DispatchEngine()
    best = engine.select_best_driver([d1, d2])
    assert best.driver_id == "drv_1"


def test_delivery_event_publisher():
    publisher = DeliveryEventPublisher()
    evt = publisher.build_event("delivery.assigned", "del_100", {"driver_id": "drv_1"})
    assert evt["event_type"] == "delivery.assigned"


def test_delivery_engine_checker():
    checker = DeliveryEngineChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
