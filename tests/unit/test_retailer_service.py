"""
Unit tests for Phase 4 Retailer Service (Schemas, Validation, and Static Checker).
"""

from __future__ import annotations

import os
import sys
from datetime import date
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/retailer-service")
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

from app.schemas.retailer import OrganizationCreate, StoreCreate, LicenseCreate
from scripts.constitution.check_retailer_service import RetailerServiceChecker


def test_organization_create_valid():
    org = OrganizationCreate(
        legal_name="Royal Spirits Private Limited",
        trade_name="Royal Wines",
        business_type="PRIVATE_LIMITED",
        gstin="29ABCDE1234F1Z5",
        pan="ABCDE1234F",
        owner_user_id="usr_ret_201",
    )
    assert org.legal_name == "Royal Spirits Private Limited"
    assert org.gstin == "29ABCDE1234F1Z5"


def test_store_create_valid():
    store = StoreCreate(
        organization_id="org_test_001",
        code="STR_KA_BLR_001",
        name="Royal Wines - Indiranagar",
        store_type="CL_2",
        address_line_1="100 Feet Road, Indiranagar",
        city="Bengaluru",
        state="Karnataka",
        pincode="560038",
        jurisdiction="IN-KA",
        latitude=12.9716,
        longitude=77.5946,
    )
    assert store.code == "STR_KA_BLR_001"
    assert store.jurisdiction == "IN-KA"


def test_license_create_valid():
    lic = LicenseCreate(
        license_number="KA/EX/CL2/2026/00842",
        license_type="CL_2",
        issuing_authority="Karnataka Excise Department",
        jurisdiction="IN-KA",
        valid_from=date(2026, 1, 1),
        valid_until=date(2026, 12, 31),
    )
    assert lic.license_number == "KA/EX/CL2/2026/00842"
    assert lic.valid_until == date(2026, 12, 31)


def test_retailer_service_checker():
    checker = RetailerServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
