import pytest
from services.inventory.app.schemas.inventory import StockReceipt
from services.inventory.app.schemas.reservation import ReservationCreate
from services.inventory.app.services.inventory_service import InventoryService
from services.inventory.app.services.reservation_service import ReservationService


@pytest.mark.asyncio
async def test_reservation_lifecycle():
    inv_svc = InventoryService()
    await inv_svc.receive_stock(
        StockReceipt(
            store_id="STORE-01",
            sku_id="SKU-100",
            quantity=5,
            idempotency_key="receipt-100",
        )
    )

    res_svc = ReservationService(inventory_service=inv_svc)

    res = await res_svc.reserve(
        ReservationCreate(
            order_id="ORD-1",
            store_id="STORE-01",
            sku_id="SKU-100",
            quantity=2,
            idempotency_key="res-key-01",
        )
    )

    assert res["status"] == "ACTIVE"
    assert res["quantity"] == 2

    avail = await inv_svc.get_available("STORE-01", "SKU-100")
    assert avail == 3

    released = await res_svc.release(res["id"])
    assert released["status"] == "RELEASED"

    avail_after_release = await inv_svc.get_available("STORE-01", "SKU-100")
    assert avail_after_release == 5
