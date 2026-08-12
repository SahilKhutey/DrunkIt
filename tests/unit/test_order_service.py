"""
Unit tests for Phase 6 Order Service (Schemas, Validation, State Machine, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/order-service")
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

from app.schemas.order import OrderCreate, OrderItemCreate, OrderStateTransitionRequest, OrderCancelRequest
from app.services.order_service import VALID_TRANSITIONS
from scripts.constitution.check_order_service import OrderServiceChecker


def test_order_create_valid():
    item = OrderItemCreate(
        sku_id="SKU_8901234567890",
        title="Amrut Fusion Single Malt Indian Whisky 750ml",
        unit_price_inr=2800.0,
        quantity=1,
    )
    ord_in = OrderCreate(
        consumer_id="usr_consumer_101",
        store_id="STR_KA_BLR_001",
        delivery_address_id="addr_101",
        jurisdiction="IN-KA",
        items=[item],
    )
    assert ord_in.consumer_id == "usr_consumer_101"
    assert len(ord_in.items) == 1


def test_order_state_machine_transitions():
    assert "COMPLIANCE_PENDING" in VALID_TRANSITIONS["DRAFT"]
    assert "COMPLIANT" in VALID_TRANSITIONS["COMPLIANCE_PENDING"]
    assert "PAYMENT_PENDING" in VALID_TRANSITIONS["COMPLIANT"]
    assert "CONFIRMED" in VALID_TRANSITIONS["PAYMENT_PENDING"]
    assert "DISPATCH_PENDING" in VALID_TRANSITIONS["CONFIRMED"]
    assert "OUT_FOR_DELIVERY" in VALID_TRANSITIONS["DISPATCH_PENDING"]
    assert "DELIVERED" in VALID_TRANSITIONS["OUT_FOR_DELIVERY"]


def test_order_service_checker():
    checker = OrderServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
