import pytest
from services.delivery.app.schemas.delivery import DeliveryCreate
from services.delivery.app.services.assignment_service import AssignmentService
from services.delivery.app.services.dispatch_service import DispatchService


@pytest.mark.asyncio
async def test_assign_rider():
    dispatch_svc = DispatchService()
    delivery = await dispatch_svc.create_delivery(
        DeliveryCreate(
            order_id="order-d11-assign",
            retailer_id="ret-d11-1",
            delivery_address_id="addr-100",
            regulated_product=True,
        )
    )
    await dispatch_svc.queue_dispatch(delivery["id"])

    assign_svc = AssignmentService(dispatch_service=dispatch_svc)
    assign_svc.riders["rider-1"] = {
        "id": "rider-1",
        "status": "AVAILABLE",
        "verification_status": "ACTIVE",
        "current_latitude": 19.0760,
        "current_longitude": 72.8777,
        "active_delivery_id": None,
    }

    assignment = await assign_svc.assign_rider(delivery["id"])
    assert assignment["rider_id"] == "rider-1"
    assert delivery["status"] == "ASSIGNED"
