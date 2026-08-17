import pytest
from services.inventory.app.schemas.inventory import StockReceipt
from services.inventory.app.services.inventory_service import InventoryService


@pytest.mark.asyncio
async def test_receive_stock_and_available():
    service = InventoryService()

    await service.receive_stock(
        StockReceipt(
            store_id="STORE-01",
            sku_id="SKU-100",
            quantity=10,
            idempotency_key="receipt-01",
        )
    )

    avail = await service.get_available("STORE-01", "SKU-100")
    assert avail == 10
