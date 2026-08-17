import pytest
from services.delivery.app.schemas.delivery import DeliveryCreate
from services.delivery.app.services.dispatch_service import DispatchService


@pytest.mark.asyncio
async def test_create_delivery_and_queue_dispatch():
    svc = DispatchService()
    delivery = await svc.create_delivery(
        DeliveryCreate(
            order_id="order-d11-1",
            retailer_id="ret-d11-1",
            delivery_address_id="addr-100",
            regulated_product=True,
        )
    )

    assert delivery["status"] == "CREATED"
    assert delivery["verification_required"] is True

    job = await svc.queue_dispatch(delivery["id"], priority=100)
    assert job["status"] == "QUEUED"
    assert delivery["status"] == "ASSIGNMENT_PENDING"
