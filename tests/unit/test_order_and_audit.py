import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/order-service")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/audit-service")))

import pytest
from order_app.main import ORDERS_DB, get_order
from audit_app.main import AUDIT_LOG_STORE, record_event, AuditEventCreate

def test_get_order_state():
    order = get_order("ORD-78219")
    assert order.order_id == "ORD-78219"
    assert order.status == "CONFIRMED"
    assert order.delivery_otp is not None

def test_audit_event_logging():
    initial_count = len(AUDIT_LOG_STORE)
    req = AuditEventCreate(
        event_type="COMPLIANCE_EVALUATION",
        actor_id="SYSTEM",
        actor_type="SYSTEM",
        action="EVALUATE_POLICY",
        resource_id="DEC-1001",
        resource_type="COMPLIANCE_DECISION",
        jurisdiction="IN-KA",
        payload={"result": "ALLOW"}
    )
    rec = record_event(req)
    assert rec.event_id.startswith("AUD-")
    assert len(rec.payload_hash) == 64  # SHA256 hex string
    assert len(AUDIT_LOG_STORE) == initial_count + 1
