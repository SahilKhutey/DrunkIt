"""Unit tests for atomic inventory reservation under concurrency."""

import asyncio
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from faccp_platform.database.base import Base
from services.fulfillment.app.models.inventory import Inventory
from services.fulfillment.app.repositories.inventory import InventoryRepository


@pytest.mark.asyncio
async def test_inventory_cannot_oversell():
    """Verify that atomic conditional SQL updates prevent stock overselling under concurrent requests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    pid = str(uuid.uuid4())
    wid = str(uuid.uuid4())

    # Initialize stock = 1
    async with session_factory() as session:
        inv = Inventory(product_id=pid, warehouse_id=wid, available_quantity=1)
        session.add(inv)
        await session.commit()

    async def try_reserve():
        async with session_factory() as session:
            repo = InventoryRepository(session)
            try:
                await repo.reserve_inventory(pid, wid, 1)
                await session.commit()
                return True
            except ValueError:
                return False

    results = await asyncio.gather(try_reserve(), try_reserve(), return_exceptions=True)
    successes = [r for r in results if r is True]

    # Exactly 1 reservation should succeed
    assert len(successes) == 1

    async with session_factory() as session:
        repo = InventoryRepository(session)
        inv = await repo.get_or_create(pid, wid)
        assert inv.available_quantity == 0
        assert inv.reserved_quantity == 1

    await engine.dispose()
