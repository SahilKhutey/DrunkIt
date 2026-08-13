import os
import sys
import pytest

service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

from app.services.inventory import (
    InventoryService,
)
from app.domain.fulfilment.planner import (
    FulfilmentPlanner,
)
from app.schemas.fulfilment import (
    FulfilmentRequest,
    OrderLine,
)
from app.schemas.location import GeoLocation


@pytest.mark.asyncio
async def test_inventory_available():

    service = InventoryService()

    result = await service.has_quantity(
        "STORE-001",
        "PROD-001",
        2,
    )

    assert result is True


@pytest.mark.asyncio
async def test_inventory_unavailable():

    service = InventoryService()

    result = await service.has_quantity(
        "STORE-001",
        "PROD-001",
        1000,
    )

    assert result is False


@pytest.mark.asyncio
async def test_fulfilment_planner_creates_plan():

    planner = FulfilmentPlanner()

    request = FulfilmentRequest(
        order_id="ORD-10001",
        customer_location=GeoLocation(latitude=21.1750, longitude=72.8350),
        items=[OrderLine(product_id="PROD-001", quantity=2)],
    )

    plan = await planner.create_plan(request)

    assert plan.order_id == "ORD-10001"
    assert plan.store_id in ["STORE-001", "STORE-002"]
    assert plan.serviceable is True
    assert plan.compliance_status == "APPROVED"
    assert plan.status == "STORE_SELECTED"
