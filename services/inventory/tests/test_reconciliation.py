import pytest
from services.inventory.app.schemas.inventory import StockReceipt
from services.inventory.app.services.inventory_service import InventoryService
from services.inventory.app.services.reconciliation_service import ReconciliationService


@pytest.mark.asyncio
async def test_reconciliation_consistency():
    inv_svc = InventoryService()
    await inv_svc.receive_stock(
        StockReceipt(
            store_id="STORE-REC",
            sku_id="SKU-REC",
            quantity=15,
            idempotency_key="receipt-rec-1",
        )
    )

    recon_svc = ReconciliationService(inventory_service=inv_svc)
    report = await recon_svc.reconcile("STORE-REC", "SKU-REC")

    assert report["ledger_stock"] == 15
    assert report["inventory_stock"] == 15
    assert report["difference"] == 0
    assert report["consistent"] is True
