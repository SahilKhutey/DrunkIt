import asyncio
import pytest

from services.inventory.app.schemas.inventory import StockReceipt
from services.inventory.app.schemas.reservation import ReservationCreate
from services.inventory.app.services.inventory_service import InventoryService
from services.inventory.app.services.reservation_service import ReservationService


@pytest.mark.asyncio
async def test_concurrent_reservation_prevent_oversell():
    inv_svc = InventoryService()
    await inv_svc.receive_stock(
        StockReceipt(
            store_id="STORE-RACE",
            sku_id="SKU-RACE",
            quantity=1,
            idempotency_key="receipt-race",
        )
    )

    res_svc = ReservationService(inventory_service=inv_svc)

    async def try_reserve(order_id: str, idempotency_key: str):
        return await res_svc.reserve(
            ReservationCreate(
                order_id=order_id,
                store_id="STORE-RACE",
                sku_id="SKU-RACE",
                quantity=1,
                idempotency_key=idempotency_key,
            )
        )

    results = await asyncio.gather(
        try_reserve("ORD-A", "key-A"),
        try_reserve("ORD-B", "key-B"),
        return_exceptions=True,
    )

    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    assert len(successes) == 1
    assert len(failures) == 1
    assert "INSUFFICIENT_STOCK" in str(failures[0])
