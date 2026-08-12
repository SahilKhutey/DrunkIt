"""Seed sample consumer profiles and delivery addresses."""

from __future__ import annotations

import asyncio
from datetime import date
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import ConsumerProfile, DeliveryAddress
from faccp_common.database import init_engine, session_scope

SAMPLE_CONSUMERS = [
    {
        "user_id": "usr_consumer_seed_101",
        "first_name": "Aarav",
        "last_name": "Sharma",
        "display_name": "Aarav S.",
        "date_of_birth": date(1998, 5, 14),
        "consumer_level": "C2_AGE_VERIFIED",
        "is_age_verified": True,
        "primary_jurisdiction": "IN-KA",
    },
    {
        "user_id": "usr_consumer_seed_102",
        "first_name": "Ananya",
        "last_name": "Patel",
        "display_name": "Ananya P.",
        "date_of_birth": date(1995, 11, 22),
        "consumer_level": "C2_AGE_VERIFIED",
        "is_age_verified": True,
        "primary_jurisdiction": "IN-MH",
    },
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for cons in SAMPLE_CONSUMERS:
            existing = await session.execute(
                select(ConsumerProfile).where(ConsumerProfile.user_id == cons["user_id"])
            )
            if existing.scalar_one_or_none() is None:
                p = ConsumerProfile(
                    user_id=cons["user_id"],
                    first_name=cons["first_name"],
                    last_name=cons["last_name"],
                    display_name=cons["display_name"],
                    date_of_birth=cons["date_of_birth"],
                    consumer_level=cons["consumer_level"],
                    is_age_verified=cons["is_age_verified"],
                    primary_jurisdiction=cons["primary_jurisdiction"],
                )
                session.add(p)
                await session.flush()

                addr = DeliveryAddress(
                    consumer_id=p.id,
                    label="Home",
                    recipient_name=f"{cons['first_name']} {cons['last_name']}",
                    recipient_phone="+919876543210",
                    address_line_1="100 Feet Road, Indiranagar",
                    city="Bengaluru",
                    state="Karnataka",
                    pincode="560038",
                    jurisdiction=cons["primary_jurisdiction"],
                    latitude=12.9716,
                    longitude=77.5946,
                    is_default=True,
                )
                session.add(addr)
                print(f"  Consumer seeded: {cons['first_name']} ({cons['user_id']})")

    print("\n[OK] Seeded consumer profiles and delivery addresses.")


if __name__ == "__main__":
    asyncio.run(seed())
