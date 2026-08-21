"""Unit test suite for the Transactional Outbox Relay Worker."""

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.uow import SyncUnitOfWork
from app.workers.outbox_relay import OutboxRelayWorker


def test_outbox_relay_worker_processes_and_dispatches_events(db_session: Session) -> None:
    """Verify outbox worker processes pending events into EventEnvelope format."""
    received_envelopes: list[dict[str, Any]] = []

    def mock_sink(envelope: dict[str, Any]) -> None:
        received_envelopes.append(envelope)

    # 1. Publish test domain events via Unit of Work
    uow = SyncUnitOfWork(db_session)
    agg_id_1 = uuid.uuid4()
    agg_id_2 = uuid.uuid4()

    uow.publish_outbox(
        event_type="INVENTORY_RESERVED",
        aggregate_type="Order",
        aggregate_id=agg_id_1,
        payload={"order_id": str(agg_id_1), "sku_count": 2},
    )
    uow.publish_outbox(
        event_type="COMPLIANCE_APPROVED",
        aggregate_type="ComplianceDecision",
        aggregate_id=agg_id_2,
        payload={"jurisdiction": "IN-WB", "status": "ALLOWED"},
    )
    uow.commit()

    # 2. Run Outbox Worker Batch
    worker = OutboxRelayWorker(batch_size=10, dispatch_sink=mock_sink)
    dispatched_count = worker.process_pending_events(db_session)

    # 3. Assertions
    assert dispatched_count >= 2
    assert len(received_envelopes) >= 2

    event_types = [e["event_type"] for e in received_envelopes]
    assert "INVENTORY_RESERVED" in event_types
    assert "COMPLIANCE_APPROVED" in event_types

    first = next(e for e in received_envelopes if e["event_type"] == "INVENTORY_RESERVED")
    assert first["aggregate_type"] == "Order"
    assert first["aggregate_id"] == str(agg_id_1)
    assert first["payload"]["sku_count"] == 2
    assert "correlation_id" in first
    assert "created_at" in first
