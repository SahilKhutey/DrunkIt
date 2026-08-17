import pytest
from services.delivery.app.schemas.delivery import DeliveryCreate
from services.delivery.app.services.dispatch_service import DispatchService
from services.delivery.app.services.verification_service import VerificationService


@pytest.mark.asyncio
async def test_verification_workflow():
    dispatch_svc = DispatchService()
    delivery = await dispatch_svc.create_delivery(
        DeliveryCreate(
            order_id="order-d11-verify",
            retailer_id="ret-d11-1",
            delivery_address_id="addr-100",
            regulated_product=True,
        )
    )

    delivery["status"] = "VERIFICATION_PENDING"

    ver_svc = VerificationService(dispatch_service=dispatch_svc)
    res = await ver_svc.verify_delivery(delivery["id"], "token_valid_123")

    assert res.status == "VERIFIED"
    assert delivery["status"] == "VERIFIED"
