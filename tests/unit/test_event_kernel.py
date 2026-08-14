"""Unit test suite for Event Kernel components."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from faccp_platform.database.base import Base
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.idempotency import EventIdempotency
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.producer import EventProducer
from faccp_platform.events.retry import RetryPolicy
from faccp_platform.events.dlq import DeadLetterPublisher
from faccp_platform.events.topics import Topics


def test_topics_all():
    all_topics = Topics.all()
    assert Topics.ORDER_EVENTS in all_topics
    assert Topics.PAYMENT_EVENTS in all_topics
    assert Topics.DEAD_LETTER in all_topics
    assert len(all_topics) >= 5


@pytest.mark.asyncio
async def test_idempotency_and_outbox_services():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        idempotency = EventIdempotency(session)
        test_event_id = uuid.uuid4()

        # Check not processed
        assert await idempotency.already_processed(test_event_id) is False

        # Mark processed
        await idempotency.mark_processed(test_event_id, consumer="payment-service")
        assert await idempotency.already_processed(test_event_id) is True

        # Test Outbox Service Enqueue
        outbox = OutboxService(session, producer=EventProducer())
        envelope = EventEnvelope(
            event_type="order.created",
            metadata=EventMetadata(producer="order-service"),
            payload={"order_id": "ord-999"},
        )
        record = await outbox.enqueue(topic=Topics.ORDER_EVENTS, event=envelope)
        assert record.status == "pending"
        assert record.topic == Topics.ORDER_EVENTS

        processed_count = await outbox.process_pending(limit=10)
        assert processed_count == 1
        assert record.status == "published"

    await engine.dispose()


@pytest.mark.asyncio
async def test_retry_policy_success_and_failure():
    policy = RetryPolicy(max_attempts=3, base_delay=0.01)

    attempts = 0
    async def flaky_op():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("Transient error")
        return "success"

    result = await policy.execute(flaky_op)
    assert result == "success"
    assert attempts == 2

    async def failing_op():
        raise RuntimeError("Fatal error")

    with pytest.raises(RuntimeError):
        await policy.execute(failing_op)
