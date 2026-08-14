"""Unit tests for compliance gate enforcement during order creation."""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from faccp_platform.database.base import Base
from services.order.app.domain.enums import OrderStatus
from services.order.app.domain.exceptions import ComplianceCheckFailedError
from services.order.app.schemas.order import CreateOrderRequest, OrderItemCreate
from services.order.app.services.order_service import OrderService


@pytest.mark.asyncio
async def test_compliance_gate_denied_blocks_order():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        mock_compliance = AsyncMock()
        mock_compliance.evaluate = AsyncMock(
            return_value={"status": "deny", "reasons": ["age_requirement_failed"]}
        )

        service = OrderService(session=session, compliance_client=mock_compliance)
        request = CreateOrderRequest(
            consumer_id=uuid.uuid4(),
            jurisdiction_id=uuid.uuid4(),
            idempotency_key="idemp_key_1234567890_test_01",
            items=[
                OrderItemCreate(
                    product_id=uuid.uuid4(),
                    product_name="Sample Whisky",
                    quantity=Decimal("1"),
                    unit_price=Decimal("1500.00"),
                )
            ],
        )

        with pytest.raises(ComplianceCheckFailedError):
            await service.create_order(request)

    await engine.dispose()


@pytest.mark.asyncio
async def test_compliance_gate_allowed_creates_order():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        mock_compliance = AsyncMock()
        mock_compliance.evaluate = AsyncMock(
            return_value={"status": "allow", "decision_id": str(uuid.uuid4()), "policy_version": "1.0.0"}
        )

        service = OrderService(session=session, compliance_client=mock_compliance)
        request = CreateOrderRequest(
            consumer_id=uuid.uuid4(),
            jurisdiction_id=uuid.uuid4(),
            idempotency_key="idemp_key_1234567890_test_02",
            items=[
                OrderItemCreate(
                    product_id=uuid.uuid4(),
                    product_name="Sample Beer",
                    quantity=Decimal("2"),
                    unit_price=Decimal("200.00"),
                )
            ],
        )

        order = await service.create_order(request)
        assert order.status == OrderStatus.PENDING_PAYMENT
        assert order.total == Decimal("400.00")

    await engine.dispose()
