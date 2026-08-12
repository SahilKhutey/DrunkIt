"""Seed sample delivery missions."""

from __future__ import annotations

import asyncio
import hashlib
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import DeliveryAssignment, DeliveryMission
from faccp_common.database import init_engine, session_scope

SAMPLE_MISSIONS = [
    {
        "mission_code": "MIS-20260812-7B",
        "order_id": "ORD-20260812-9A8B",
        "store_id": "STR_KA_BLR_001",
        "consumer_id": "usr_consumer_seed_101",
        "status": "ASSIGNED",
        "otp": "4829",
        "pickup_address": "Royal Wines, 100ft Road, Indiranagar",
        "dropoff_address": "Indiranagar 12th Main, Bengaluru",
        "driver_id": "drv_agent_seed_501",
    }
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for m in SAMPLE_MISSIONS:
            existing = await session.execute(
                select(DeliveryMission).where(DeliveryMission.mission_code == m["mission_code"])
            )
            if existing.scalar_one_or_none() is None:
                otp_hash = hashlib.sha256(m["otp"].encode()).hexdigest()
                mission = DeliveryMission(
                    mission_code=m["mission_code"],
                    order_id=m["order_id"],
                    store_id=m["store_id"],
                    consumer_id=m["consumer_id"],
                    status=m["status"],
                    delivery_otp_hash=otp_hash,
                    pickup_address=m["pickup_address"],
                    dropoff_address=m["dropoff_address"],
                    assigned_driver_id=m["driver_id"],
                )
                session.add(mission)
                await session.flush()

                assign = DeliveryAssignment(
                    mission_id=mission.id,
                    driver_id=m["driver_id"],
                    status="ACCEPTED",
                )
                session.add(assign)
                print(f"  Delivery mission seeded: {m['mission_code']} (Driver: {m['driver_id']})")

    print("\n[OK] Seeded delivery missions.")


if __name__ == "__main__":
    asyncio.run(seed())
