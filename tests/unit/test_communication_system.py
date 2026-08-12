"""
Unit tests for Communication System Architecture (5 Layers, Envelopes, Retry, Permissions, Correlation).
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from faccp_common.communication import (
    StandardRequest, StandardEvent, RetryPolicy, IdempotentConsumer,
    ServicePermissionMatrix, CorrelationContext
)
from scripts.constitution.check_communication_system import CommunicationSystemChecker


def test_standard_request_envelope():
    req = StandardRequest(
        source="checkout-service",
        actor_type="consumer",
        actor_id="usr_123",
        payload={"item_count": 2},
    )
    d = req.to_dict()
    assert d["source"] == "checkout-service"
    assert d["actor"]["id"] == "usr_123"

    headers = req.to_headers()
    assert "X-Request-ID" in headers
    assert headers["X-Actor-Type"] == "consumer"


def test_standard_event_envelope():
    evt = StandardEvent(
        event_type="order.created",
        producer="order-service",
        payload={"order_id": "ord_100"},
    )
    d = evt.to_dict()
    assert d["event_type"] == "order.created"
    assert d["producer"] == "order-service"
    assert d["event_id"].startswith("evt_")


def test_retry_policy():
    delay_0 = RetryPolicy.get_delay(0)
    delay_1 = RetryPolicy.get_delay(1)
    assert delay_0 >= 0.0
    assert delay_1 >= 0.0


def test_service_permission_matrix():
    assert ServicePermissionMatrix.is_allowed("checkout-service", "inventory-service", "reserve") is True
    assert ServicePermissionMatrix.is_allowed("consumer-service", "payment-service", "create_intent") is False


@pytest.mark.asyncio
async def test_idempotent_consumer():
    consumer = IdempotentConsumer()
    evt = {"event_id": "evt_test123", "payload": {}}

    res1 = await consumer.process(evt)
    assert res1 is True

    res2 = await consumer.process(evt)
    assert res2 is False


def test_correlation_context():
    ctx = CorrelationContext()
    assert ctx.correlation_id.startswith("corr_")
    child = ctx.child()
    assert child.correlation_id == ctx.correlation_id
    assert child.causation_id.startswith("req_")


def test_communication_system_checker():
    checker = CommunicationSystemChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
