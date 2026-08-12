"""Seed sample preference profiles and affinity scores."""

from __future__ import annotations

import asyncio
import json
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import ConsumerPreferenceProfile, ProductAffinityScore
from faccp_common.database import init_engine, session_scope

SAMPLE_PROFILES = [
    {
        "consumer_id": "usr_consumer_seed_101",
        "preferred_categories": ["WHISKY", "CRAFT_BEER"],
        "preferred_brands": ["GLENFIDDICH", "BIRA91"],
        "price_sensitivity_score": 0.35,
    }
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for p in SAMPLE_PROFILES:
            existing = await session.execute(
                select(ConsumerPreferenceProfile).where(
                    ConsumerPreferenceProfile.consumer_id == p["consumer_id"]
                )
            )
            if existing.scalar_one_or_none() is None:
                prof = ConsumerPreferenceProfile(
                    consumer_id=p["consumer_id"],
                    preferred_categories_json=json.dumps(p["preferred_categories"]),
                    preferred_brands_json=json.dumps(p["preferred_brands"]),
                    price_sensitivity_score=p["price_sensitivity_score"],
                )
                session.add(prof)
                print(f"  Preference profile seeded for {p['consumer_id']}")

        aff = ProductAffinityScore(
            sku_id_a="SKU_SINGLE_MALT_12Y_750ML",
            sku_id_b="SKU_CRAFT_BEER_IPA_6PK",
            affinity_score=0.82,
        )
        session.add(aff)

    print("\n[OK] Seeded recommendation profiles and affinity scores.")


if __name__ == "__main__":
    asyncio.run(seed())
