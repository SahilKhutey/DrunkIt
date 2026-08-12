"""Seed sample inventory balances."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import InventoryAuditLog, InventoryItem
from faccp_common.database import init_engine, session_scope

SAMPLE_INVENTORY = [
    {
        "store_id": "STR_KA_BLR_001",
        "sku_id": "SKU_8901234567890",
        "available_quantity": 50,
        "reorder_level": 10,
    },
    {
        "store_id": "STR_KA_BLR_001",
        "sku_id": "SKU_8901234567891",
        "available_quantity": 120,
        "reorder_level": 20,
    },
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for inv in SAMPLE_INVENTORY:
            existing = await session.execute(
                select(InventoryItem).where(
                    InventoryItem.store_id == inv["store_id"],
                    InventoryItem.sku_id == inv["sku_id"],
                )
            )
            if existing.scalar_one_or_none() is None:
                item = InventoryItem(
                    store_id=inv["store_id"],
                    sku_id=inv["sku_id"],
                    available_quantity=inv["available_quantity"],
                    reserved_quantity=0,
                    reorder_level=inv["reorder_level"],
                    is_active=True,
                )
                session.add(item)
                await session.flush()

                audit = InventoryAuditLog(
                    store_id=inv["store_id"],
                    sku_id=inv["sku_id"],
                    action="RESTOCK",
                    quantity_change=inv["available_quantity"],
                    resulting_balance=inv["available_quantity"],
                    performed_by="seed_script",
                )
                session.add(audit)
                print(f"  Inventory seeded for store {inv['store_id']} SKU {inv['sku_id']}: {inv['available_quantity']} units")

    print("\n[OK] Seeded store inventory balances.")


if __name__ == "__main__":
    asyncio.run(seed())
