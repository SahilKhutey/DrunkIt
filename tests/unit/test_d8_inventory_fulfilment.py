"""
Master unit test for Phase D8 Inventory + Store Fulfilment Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.inventory.app.schemas.inventory import StockReceipt
from services.inventory.app.schemas.reservation import ReservationCreate
from services.inventory.app.services.fulfilment_service import FulfilmentService
from services.inventory.app.services.inventory_service import InventoryService
from services.inventory.app.services.reservation_service import ReservationService


@pytest.mark.asyncio
async def test_d8_inventory_and_fulfilment_flow():
    inv_svc = InventoryService()
    res_svc = ReservationService(inventory_service=inv_svc)
    ful_svc = FulfilmentService()

    # Receive stock
    await inv_svc.receive_stock(
        StockReceipt(
            store_id="STORE-MUMBAI",
            sku_id="SKU-ROYAL-750ML",
            quantity=20,
            idempotency_key="receipt-master-1",
        )
    )

    avail = await inv_svc.get_available("STORE-MUMBAI", "SKU-ROYAL-750ML")
    assert avail == 20

    # Reserve stock
    res = await res_svc.reserve(
        ReservationCreate(
            order_id="ORD-9999",
            store_id="STORE-MUMBAI",
            sku_id="SKU-ROYAL-750ML",
            quantity=3,
            idempotency_key="res-master-1",
        )
    )
    assert res["status"] == "ACTIVE"

    avail_remaining = await inv_svc.get_available("STORE-MUMBAI", "SKU-ROYAL-750ML")
    assert avail_remaining == 17

    # Create fulfilment record & transition
    ful = await ful_svc.create(order_id="ORD-9999", store_id="STORE-MUMBAI")
    assert ful["status"] == "CREATED"

    picking = await ful_svc.transition(ful["id"], "PICKING")
    assert picking["status"] == "PICKING"

    picked = await ful_svc.transition(ful["id"], "PICKED")
    assert picked["status"] == "PICKED"

    packing = await ful_svc.transition(ful["id"], "PACKING")
    assert packing["status"] == "PACKING"

    packed = await ful_svc.transition(ful["id"], "PACKED")
    assert packed["status"] == "PACKED"

    ready = await ful_svc.transition(ful["id"], "READY_FOR_HANDOFF")
    assert ready["status"] == "READY_FOR_HANDOFF"

    handed = await ful_svc.transition(ful["id"], "HANDED_TO_DELIVERY")
    assert handed["status"] == "HANDED_TO_DELIVERY"
