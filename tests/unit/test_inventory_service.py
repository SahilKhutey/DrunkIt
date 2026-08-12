"""
Unit tests for Phase 5 Inventory Service (Schemas, Validation, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/inventory-service")
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

from app.schemas.inventory import StockUpdate, ReservationRequest, ReleaseRequest, DeductRequest
from scripts.constitution.check_inventory_service import InventoryServiceChecker


def test_stock_update_valid():
    stock = StockUpdate(
        store_id="STR_KA_BLR_001",
        sku_id="SKU_8901234567890",
        quantity=50,
        reorder_level=10,
    )
    assert stock.store_id == "STR_KA_BLR_001"
    assert stock.quantity == 50


def test_reservation_request_valid():
    res = ReservationRequest(
        store_id="STR_KA_BLR_001",
        sku_id="SKU_8901234567890",
        quantity=2,
    )
    assert res.quantity == 2


def test_inventory_service_checker():
    checker = InventoryServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
