"""Integration tests for end-to-end distributed saga orchestration and compensation workflows."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from faccp_platform.database.base import Base
from faccp_platform.events.topics import Topics
from faccp_platform.saga.enums import SagaState
from faccp_platform.saga.orchestrator import OrderSaga


@pytest.mark.asyncio
async def test_complete_order_lifecycle():
    """Verify full forward saga orchestration from order created to order completed."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    oid = str(uuid.uuid4())

    async with session_factory() as session:
        saga = OrderSaga(session)

        # 1. Order created -> Compliance pending
        await saga.handle({"event_type": Topics.ORDER_CREATED, "order_id": oid})
        # 2. Compliance approved -> Risk pending
        await saga.handle({"event_type": Topics.COMPLIANCE_APPROVED, "order_id": oid})
        # 3. Risk approved -> Payment pending
        await saga.handle({"event_type": Topics.RISK_APPROVED, "order_id": oid})
        # 4. Payment captured -> Inventory pending
        await saga.handle({"event_type": Topics.PAYMENT_CAPTURED, "order_id": oid})
        # 5. Inventory reserved -> Fulfillment pending
        await saga.handle({"event_type": Topics.INVENTORY_RESERVED, "order_id": oid})
        # 6. Fulfillment ready -> Delivery pending
        await saga.handle({"event_type": Topics.FULFILLMENT_READY, "order_id": oid})
        # 7. Delivery arrived -> Verification pending
        await saga.handle({"event_type": Topics.DELIVERY_ARRIVED, "order_id": oid})
        # 8. Verification completed (passed) -> Order Completed
        await saga.handle({"event_type": Topics.VERIFICATION_COMPLETED, "order_id": oid, "status": "passed"})

        await session.commit()

    async with session_factory() as session:
        instance = await OrderSaga(session).get_or_create_saga(oid)
        assert instance.state == SagaState.COMPLETED

    await engine.dispose()


@pytest.mark.asyncio
async def test_inventory_failure_compensates_payment():
    """Verify compensation flow when inventory fails after payment capture."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    oid = str(uuid.uuid4())

    async with session_factory() as session:
        saga = OrderSaga(session)

        # 1. Order created & Payment captured
        await saga.handle({"event_type": Topics.ORDER_CREATED, "order_id": oid})
        await saga.handle({"event_type": Topics.PAYMENT_CAPTURED, "order_id": oid})

        # 2. Inventory fails
        await saga.handle({"event_type": Topics.INVENTORY_FAILED, "order_id": oid})
        instance = await saga.get_or_create_saga(oid)
        assert instance.state == SagaState.COMPENSATING

        # 3. Payment refunded -> Order cancelled
        await saga.handle({"event_type": Topics.PAYMENT_REFUNDED, "order_id": oid})
        assert instance.state == SagaState.FAILED

        await session.commit()

    await engine.dispose()
