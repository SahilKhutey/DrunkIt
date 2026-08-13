"""
Master unit test for Phase D11 Delivery / Dispatch / Last-Mile Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.delivery.app.schemas.delivery import DeliveryCreate
from services.delivery.app.services.assignment_service import AssignmentService
from services.delivery.app.services.delivery_service import DeliveryService
from services.delivery.app.services.dispatch_service import DispatchService
from services.delivery.app.services.pod_service import PodService
from services.delivery.app.services.verification_service import VerificationService


@pytest.mark.asyncio
async def test_full_d11_delivery_lastmile_pipeline():
    dispatch_svc = DispatchService()

    # 1. Create Delivery
    delivery = await dispatch_svc.create_delivery(
        DeliveryCreate(
            order_id="order-d11-master-pipeline",
            retailer_id="ret-surat-01",
            delivery_address_id="addr-555",
            regulated_product=True,
        )
    )
    assert delivery["status"] == "CREATED"

    # 2. Queue Dispatch
    job = await dispatch_svc.queue_dispatch(delivery["id"])
    assert job["status"] == "QUEUED"

    # 3. Rider Assignment
    assign_svc = AssignmentService(dispatch_service=dispatch_svc)
    assign_svc.riders["rider-surat-1"] = {
        "id": "rider-surat-1",
        "status": "AVAILABLE",
        "verification_status": "ACTIVE",
        "current_latitude": 21.1702,
        "current_longitude": 72.8311,
        "active_delivery_id": None,
    }
    assignment = await assign_svc.assign_rider(delivery["id"])
    assert assignment["rider_id"] == "rider-surat-1"

    # 4. Progress Delivery (Pickup -> In Transit -> Arriving)
    del_svc = DeliveryService(dispatch_service=dispatch_svc)
    await dispatch_svc.transition(delivery, "PICKUP_PENDING")
    await dispatch_svc.transition(delivery, "PICKED_UP")
    await dispatch_svc.transition(delivery, "IN_TRANSIT")
    await dispatch_svc.transition(delivery, "ARRIVING")
    await dispatch_svc.transition(delivery, "VERIFICATION_PENDING")

    # 5. Regulatory Verification Gate
    ver_svc = VerificationService(dispatch_service=dispatch_svc)
    ver_res = await ver_svc.verify_delivery(delivery["id"], "token_valid_surat")
    assert ver_res.status == "VERIFIED"

    # 6. Handover & Proof of Delivery Completion
    handed = await del_svc.handover(delivery["id"])
    assert handed["status"] == "HANDED_OVER"

    pod_svc = PodService(delivery_service=del_svc)
    pod = await pod_svc.complete_delivery(delivery["id"])
    assert pod["delivery_id"] == delivery["id"]
    assert delivery["status"] == "COMPLETED"
