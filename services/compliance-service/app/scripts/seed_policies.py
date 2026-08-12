"""Seed state-level alcohol compliance policies and dry days."""

from __future__ import annotations

import asyncio
from datetime import date, datetime, time, timezone
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import DryDayCalendar, Policy
from faccp_common.database import init_engine, session_scope

STATE_POLICIES = [
    {
        "code": "POL_KA_ALCOHOL_2026",
        "title": "Karnataka Excise Alcohol Policy 2026",
        "jurisdiction": "IN-KA",
        "min_purchasing_age": 21,
        "max_volume_per_transaction_ml": 4500,
        "sales_start_time": time(10, 0),
        "sales_end_time": time(22, 30),
    },
    {
        "code": "POL_MH_ALCOHOL_2026",
        "title": "Maharashtra Prohibition & Excise Policy 2026",
        "jurisdiction": "IN-MH",
        "min_purchasing_age": 25,
        "max_volume_per_transaction_ml": 3000,
        "sales_start_time": time(10, 0),
        "sales_end_time": time(22, 0),
    },
    {
        "code": "POL_DL_ALCOHOL_2026",
        "title": "Delhi Excise Alcohol Policy 2026",
        "jurisdiction": "IN-DL",
        "min_purchasing_age": 21,
        "max_volume_per_transaction_ml": 9000,
        "sales_start_time": time(10, 0),
        "sales_end_time": time(22, 0),
    },
    {
        "code": "POL_TG_ALCOHOL_2026",
        "title": "Telangana Prohibition & Excise Policy 2026",
        "jurisdiction": "IN-TG",
        "min_purchasing_age": 21,
        "max_volume_per_transaction_ml": 4500,
        "sales_start_time": time(10, 0),
        "sales_end_time": time(23, 0),
    },
]

NATIONAL_DRY_DAYS = [
    {"jurisdiction": "IN-KA", "dry_date": date(2026, 1, 26), "occasion": "Republic Day"},
    {"jurisdiction": "IN-KA", "dry_date": date(2026, 8, 15), "occasion": "Independence Day"},
    {"jurisdiction": "IN-KA", "dry_date": date(2026, 10, 2), "occasion": "Gandhi Jayanti"},
    {"jurisdiction": "IN-MH", "dry_date": date(2026, 1, 26), "occasion": "Republic Day"},
    {"jurisdiction": "IN-MH", "dry_date": date(2026, 8, 15), "occasion": "Independence Day"},
    {"jurisdiction": "IN-MH", "dry_date": date(2026, 10, 2), "occasion": "Gandhi Jayanti"},
    {"jurisdiction": "IN-DL", "dry_date": date(2026, 1, 26), "occasion": "Republic Day"},
    {"jurisdiction": "IN-DL", "dry_date": date(2026, 8, 15), "occasion": "Independence Day"},
    {"jurisdiction": "IN-DL", "dry_date": date(2026, 10, 2), "occasion": "Gandhi Jayanti"},
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for pol in STATE_POLICIES:
            existing = await session.execute(
                select(Policy).where(Policy.code == pol["code"])
            )
            if existing.scalar_one_or_none() is None:
                p = Policy(
                    code=pol["code"],
                    title=pol["title"],
                    jurisdiction=pol["jurisdiction"],
                    category="alcohol",
                    effective_from=datetime.now(timezone.utc),
                    min_purchasing_age=pol["min_purchasing_age"],
                    max_volume_per_transaction_ml=pol["max_volume_per_transaction_ml"],
                    sales_start_time=pol["sales_start_time"],
                    sales_end_time=pol["sales_end_time"],
                )
                session.add(p)
                print(f"  Policy seeded: {pol['code']} ({pol['jurisdiction']})")

        for dry in NATIONAL_DRY_DAYS:
            existing = await session.execute(
                select(DryDayCalendar).where(
                    DryDayCalendar.jurisdiction == dry["jurisdiction"],
                    DryDayCalendar.dry_date == dry["dry_date"],
                )
            )
            if existing.scalar_one_or_none() is None:
                d = DryDayCalendar(
                    jurisdiction=dry["jurisdiction"],
                    dry_date=dry["dry_date"],
                    occasion=dry["occasion"],
                    is_full_day=True,
                )
                session.add(d)
                print(f"  Dry day seeded: {dry['jurisdiction']} on {dry['dry_date']} ({dry['occasion']})")

    print("\n[OK] Seeded alcohol compliance policies and dry-day calendar.")


if __name__ == "__main__":
    asyncio.run(seed())
