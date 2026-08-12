"""Seed sample regulatory order and state machine history."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import Order, OrderItem, OrderStateHistory
from faccp_common.database import init_engine, session_scope

SAMPLE_ORDERS = [
    {
        "order_number": "ORD-20260812-9A8B",
        "consumer_id": "usr_consumer_seed_101",
        "store_id": "STR_KA_BLR_001",
        "delivery_address_id": "addr_seed_001",
        "jurisdiction": "IN-KA",
        "order_state": "CONFIRMED",
        "total_amount_inr": 2850.0,
        "items": [
            {
                "sku_id": "SKU_8901234567890",
                "title": "Amrut Fusion Single Malt Indian Whisky 750ml",
                "unit_price_inr": 2800.0,
                "quantity": 1,
                "subtotal_inr": 2800.0,
            }
        ]
    }
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for ord_in in SAMPLE_ORDERS:
            existing = await session.execute(
                select(Order).where(Order.order_number == ord_in["order_number"])
            )
            if existing.scalar_one_or_none() is None:
                order = Order(
                    order_number=ord_in["order_number"],
                    consumer_id=ord_in["consumer_id"],
                    store_id=ord_in["store_id"],
                    delivery_address_id=ord_in["delivery_address_id"],
                    jurisdiction=ord_in["jurisdiction"],
                    order_state=ord_in["order_state"],
                    total_amount_inr=ord_in["total_amount_inr"],
                    delivery_fee_inr=50.0,
                )
                session.add(order)
                await session.flush()

                for item in ord_in["items"]:
                    oi = OrderItem(
                        order_id=order.id,
                        sku_id=item["sku_id"],
                        title=item["title"],
                        unit_price_inr=item["unit_price_inr"],
                        quantity=item["quantity"],
                        subtotal_inr=item["subtotal_inr"],
                    )
                    session.add(oi)

                hist = OrderStateHistory(
                    order_id=order.id,
                    from_state="DRAFT",
                    to_state=ord_in["order_state"],
                    triggered_by="seed_script",
                    notes="Seeded confirmed order",
                )
                session.add(hist)
                print(f"  Order seeded: {ord_in['order_number']} ({ord_in['order_state']})")

    print("\n[OK] Seeded regulatory orders.")


if __name__ == "__main__":
    asyncio.run(seed())
