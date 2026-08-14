"""Unit test for order saga compensation behavior on failure."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from faccp_platform.database.base import Base
from faccp_platform.events.topics import Topics
from faccp_platform.saga.enums import SagaState
from faccp_platform.saga.orchestrator import OrderSaga


@pytest.mark.asyncio
async def test_inventory_failure_triggers_refund():
    """Verify that inventory reservation failure transitions saga to COMPENSATING and enqueues payment.refund_requested."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    oid = str(uuid.uuid4())
    async with session_factory() as session:
        saga = OrderSaga(session)
        event = {"event_type": Topics.INVENTORY_FAILED, "order_id": oid}
        await saga.handle(event)
        await session.commit()

    async with session_factory() as session:
        saga_inst = await OrderSaga(session).get_or_create_saga(oid)
        assert saga_inst.state == SagaState.COMPENSATING

        # Check that compensation outbox event was enqueued
        res = await session.execute(Base.metadata.tables["event_outbox"].select())
        rows = res.fetchall()
        assert any(r.event_type == Topics.PAYMENT_REFUND_REQUESTED for r in rows)

    await engine.dispose()
