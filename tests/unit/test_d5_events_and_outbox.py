"""
Unit tests for Phase D5 Events, Outbox, and Atomic Reservation.
"""

from __future__ import annotations

import os
import sys
from unittest.mock import AsyncMock, MagicMock
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from packages.events.contracts import EventEnvelope
from packages.events.factory import create_event
from packages.events.publisher import enqueue_event
from packages.events.types import EventType


def test_create_event_factory():
    event = create_event(
        event_type=EventType.INVENTORY_RESERVED,
        aggregate_type="inventory",
        aggregate_id="STORE-001:PROD-001",
        payload={"quantity": 2, "order_id": "ORD-1001"},
    )

    assert isinstance(event, EventEnvelope)
    assert event.event_type == "inventory.reserved"
    assert event.aggregate_type == "inventory"
    assert event.aggregate_id == "STORE-001:PROD-001"
    assert event.payload["quantity"] == 2


@pytest.mark.asyncio
async def test_enqueue_event_outbox():
    mock_session = MagicMock()

    event = create_event(
        event_type=EventType.DELIVERY_CREATED,
        aggregate_type="delivery",
        aggregate_id="DEL-99",
        payload={"status": "PLANNING"},
    )

    await enqueue_event(mock_session, event)

    assert mock_session.add.called
    added_obj = mock_session.add.call_args[0][0]
    assert added_obj.event_type == "delivery.created"
    assert added_obj.aggregate_id == "DEL-99"
