import pytest
from services.delivery.app.schemas.delivery import DeliveryCreate
from services.delivery.app.services.delivery_service import DeliveryService
from services.delivery.app.services.dispatch_service import DispatchService
from services.delivery.app.services.pod_service import PodService


@pytest.mark.asyncio
async def test_proof_of_delivery_completion():
    dispatch_svc = DispatchService()
    delivery = await dispatch_svc.create_delivery(
        DeliveryCreate(
            order_id="order-d11-pod",
            retailer_id="ret-d11-1",
            delivery_address_id="addr-100",
            regulated_product=True,
        )
    )

    delivery["status"] = "HANDED_OVER"

    del_svc = DeliveryService(dispatch_service=dispatch_svc)
    pod_svc = PodService(delivery_service=del_svc)

    pod = await pod_svc.complete_delivery(delivery["id"])
    assert pod["delivery_id"] == delivery["id"]
    assert delivery["status"] == "COMPLETED"
