"""Unit test for outbox worker retry resilience after Kafka failure."""

import uuid
import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from faccp_platform.database.base import Base
from faccp_platform.events.outbox import enqueue_event
from faccp_platform.events.outbox_worker import OutboxWorker
from faccp_platform.events.producer import EventProducer


@pytest.mark.asyncio
async def test_outbox_retries_after_kafka_failure():
    """Verify that outbox worker retries until Kafka succeeds and sets status='published' only on success."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    producer = EventProducer()
    producer.publish = AsyncMock(
        side_effect=[
            RuntimeError("Kafka down"),
            RuntimeError("Kafka down"),
            None,
        ]
    )

    agg_id = uuid.uuid4()
    async with session_factory() as session:
        await enqueue_event(
            session,
            topic="order.created",
            event_type="order.created",
            aggregate_id=agg_id,
            payload={"order_id": str(agg_id)},
        )
        await session.commit()

    worker = OutboxWorker(session_factory, producer)

    # Attempt 1 -> Fails
    count1 = await worker.run()
    assert count1 == 0

    # Attempt 2 -> Fails
    count2 = await worker.run()
    assert count2 == 0

    # Attempt 3 -> Succeeds
    count3 = await worker.run()
    assert count3 == 1

    async with session_factory() as session:
        result = await session.execute(Base.metadata.tables["event_outbox"].select())
        row = result.fetchone()
        assert row.status == "published"

    await engine.dispose()
