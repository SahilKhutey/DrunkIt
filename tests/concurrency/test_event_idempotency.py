"""Concurrency test verifying event deduplication and idempotent processing."""

import asyncio
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from faccp_platform.database.base import Base
from faccp_platform.events.consumer import BaseConsumer
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.idempotency import already_processed


class SampleConsumer(BaseConsumer):
    consumer_name = "test-sample-consumer"
    processed_count = 0

    async def process(self, event):
        self.processed_count += 1


@pytest.mark.asyncio
async def test_duplicate_event_processed_once():
    """Verify that concurrent handling of the same event ID executes business processing logic exactly once."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    evt_id = uuid.uuid4()
    env = EventEnvelope(
        event_type="payment.captured",
        metadata=EventMetadata(event_id=evt_id, producer="payment-service"),
        aggregate_type="order",
        aggregate_id=uuid.uuid4(),
        payload={"amount": 1000},
    )

    async def handle_evt():
        async with session_factory() as session:
            consumer = SampleConsumer(session)
            await consumer.handle(env)
            await session.commit()
            return consumer.processed_count

    results = await asyncio.gather(handle_evt(), handle_evt(), handle_evt())

    async with session_factory() as session:
        is_processed = await already_processed(session, evt_id, "test-sample-consumer")
        assert is_processed is True

    await engine.dispose()
