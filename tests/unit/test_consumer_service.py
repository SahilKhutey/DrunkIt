"""
Unit tests for Phase 3 Consumer Service (Schemas, Validation, and Static Checker).
"""

from __future__ import annotations

import os
import sys
from datetime import date
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/consumer-service")
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

from app.schemas.consumer import ConsumerProfileCreate, AddressCreate, AgeVerificationSubmit
from scripts.constitution.check_consumer_service import ConsumerServiceChecker


def test_consumer_profile_create_valid():
    cp = ConsumerProfileCreate(
        user_id="usr_test_101",
        first_name="Aarav",
        last_name="Sharma",
        date_of_birth=date(1998, 5, 14),
        primary_jurisdiction="IN-KA",
    )
    assert cp.user_id == "usr_test_101"
    assert cp.first_name == "Aarav"


def test_address_create_valid():
    addr = AddressCreate(
        label="Home",
        recipient_name="Aarav Sharma",
        recipient_phone="+919876543210",
        address_line_1="100 Feet Road, Indiranagar",
        city="Bengaluru",
        state="Karnataka",
        pincode="560038",
        jurisdiction="IN-KA",
        latitude=12.9716,
        longitude=77.5946,
    )
    assert addr.city == "Bengaluru"
    assert addr.pincode == "560038"


def test_consumer_service_checker():
    checker = ConsumerServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
