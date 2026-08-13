"""
Unit tests for Master Phase D1 Delivery Core Service & State Machine auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_delivery_core_service import (
    DeliveryCoreServiceChecker,
    DELIVERY_CORE_MAP,
)


def test_delivery_core_service_auditor_report():
    checker = DeliveryCoreServiceChecker(root_dir=root_dir)
    res = checker.audit_delivery_core_service()

    assert res["total_modules"] == 10
    assert res["verified_modules"] == 10
    assert res["score_pct"] == 100.0
    assert len(DELIVERY_CORE_MAP) == 10

    # Test key modules across State Machine, ORMs, Schemas, Repositories, Services, APIs
    assert DELIVERY_CORE_MAP["DEL-D1-01"] == "DeliveryStatus Enum (14 States)"
    assert DELIVERY_CORE_MAP["DEL-D1-02"] == "ActorType Enum (5 Actor Types)"
    assert DELIVERY_CORE_MAP["DEL-D1-03"] == "State Machine Transitions Graph & Validation Engine"
    assert DELIVERY_CORE_MAP["DEL-D1-04"] == "Delivery ORM Model (id, order_id, retailer_id, store_id, consumer_id, driver_id, addresses, status)"
    assert DELIVERY_CORE_MAP["DEL-D1-05"] == "DeliveryEvent ORM Model (id, delivery_id, event_type, actor_type, actor_id, payload, created_at)"
    assert DELIVERY_CORE_MAP["DEL-D1-07"] == "DeliveryService Layer (create_delivery, transition, assign_driver, _record_event)"
    assert DELIVERY_CORE_MAP["DEL-D1-09"] == "FastAPI REST Router (/deliveries, /{id}, /{id}/transition, /{id}/assign-driver)"
