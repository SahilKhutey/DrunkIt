"""
Unit tests for Phase 7 Delivery Service (Schemas, Validation, OTP, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/delivery-service")
common_path = os.path.join(root_dir, "services/_common")

for mod_name in list(sys.modules.keys()):
    if mod_name == "app" or mod_name.startswith("app."):
        del sys.modules[mod_name]

if service_path not in sys.path:
    sys.path.insert(0, service_path)
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.schemas.delivery import MissionCreate, DriverAssignRequest, LocationPingRequest, DeliveryCompleteRequest
from scripts.constitution.check_delivery_service import DeliveryServiceChecker


def test_mission_create_valid():
    mission = MissionCreate(
        order_id="ORD-20260812-9A8B",
        store_id="STR_KA_BLR_001",
        consumer_id="usr_consumer_101",
        pickup_address="Royal Wines, Indiranagar",
        dropoff_address="12th Main, Indiranagar",
    )
    assert mission.order_id == "ORD-20260812-9A8B"
    assert mission.store_id == "STR_KA_BLR_001"


def test_location_ping_valid():
    ping = LocationPingRequest(
        driver_id="drv_agent_501",
        latitude=12.9716,
        longitude=77.5946,
    )
    assert ping.driver_id == "drv_agent_501"


def test_delivery_complete_otp_valid():
    comp = DeliveryCompleteRequest(
        otp="4829",
    )
    assert comp.otp == "4829"


def test_delivery_service_checker():
    checker = DeliveryServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
