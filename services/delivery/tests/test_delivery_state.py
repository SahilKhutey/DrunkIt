import pytest
from services.delivery.app.schemas.delivery import DeliveryCreate
from services.delivery.app.services.delivery_service import DeliveryService
from services.delivery.app.services.dispatch_service import DispatchService


@pytest.mark.asyncio
async def test_handover_blocked_without_verification():
    dispatch_svc = DispatchService()
    delivery = await dispatch_svc.create_delivery(
        DeliveryCreate(
            order_id="order-d11-block",
            retailer_id="ret-d11-1",
            delivery_address_id="addr-100",
            regulated_product=True,
        )
    )

    delivery_svc = DeliveryService(dispatch_service=dispatch_svc)

    with pytest.raises(ValueError, match="FINAL_VERIFICATION_REQUIRED"):
        await delivery_svc.handover(delivery["id"])
