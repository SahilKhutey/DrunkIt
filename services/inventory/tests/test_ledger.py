import pytest
from services.inventory.app.schemas.inventory import StockReceipt
from services.inventory.app.services.inventory_service import InventoryService


@pytest.mark.asyncio
async def test_ledger_idempotency():
    inv_svc = InventoryService()

    rec1 = await inv_svc.receive_stock(
        StockReceipt(
            store_id="STORE-01",
            sku_id="SKU-200",
            quantity=10,
            idempotency_key="idempotent-receipt-1",
        )
    )

    rec2 = await inv_svc.receive_stock(
        StockReceipt(
            store_id="STORE-01",
            sku_id="SKU-200",
            quantity=10,
            idempotency_key="idempotent-receipt-1",
        )
    )

    # Should not duplicate stock receipt
    avail = await inv_svc.get_available("STORE-01", "SKU-200")
    assert avail == 10
