import pytest
from services.delivery.app.schemas.delivery import DeliveryCreate
from services.delivery.app.services.dispatch_service import DispatchService


@pytest.mark.asyncio
async def test_create_delivery_idempotency():
    svc = DispatchService()
    data = DeliveryCreate(
        order_id="order-d11-idemp",
        retailer_id="ret-d11-1",
        delivery_address_id="addr-100",
        regulated_product=True,
    )

    first = await svc.create_delivery(data)
    second = await svc.create_delivery(data)

    assert first["id"] == second["id"]
