"""Seed sample retailer organization, stores, and licenses."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import RetailerOrganization, Store, StoreLicense
from faccp_common.database import init_engine, session_scope

SAMPLE_RETAILERS = [
    {
        "legal_name": "Royal Spirits Private Limited",
        "trade_name": "Royal Wines Indiranagar",
        "business_type": "PRIVATE_LIMITED",
        "gstin": "29ABCDE1234F1Z5",
        "pan": "ABCDE1234F",
        "owner_user_id": "usr_retailer_seed_201",
        "store_code": "STR_KA_BLR_001",
        "store_name": "Royal Wines - 100ft Road",
        "license_number": "KA/EX/CL2/2026/00842",
        "jurisdiction": "IN-KA",
    },
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for ret in SAMPLE_RETAILERS:
            existing = await session.execute(
                select(RetailerOrganization).where(RetailerOrganization.gstin == ret["gstin"])
            )
            if existing.scalar_one_or_none() is None:
                org = RetailerOrganization(
                    legal_name=ret["legal_name"],
                    trade_name=ret["trade_name"],
                    business_type=ret["business_type"],
                    gstin=ret["gstin"],
                    pan=ret["pan"],
                    owner_user_id=ret["owner_user_id"],
                    seller_level="S2_LICENSED",
                    is_active=True,
                    is_verified=True,
                )
                session.add(org)
                await session.flush()

                store = Store(
                    organization_id=org.id,
                    code=ret["store_code"],
                    name=ret["store_name"],
                    store_type="CL_2",
                    address_line_1="100 Feet Road, Indiranagar",
                    city="Bengaluru",
                    state="Karnataka",
                    pincode="560038",
                    jurisdiction=ret["jurisdiction"],
                    latitude=12.9716,
                    longitude=77.5946,
                    is_active=True,
                    is_accepting_orders=True,
                )
                session.add(store)
                await session.flush()

                lic = StoreLicense(
                    store_id=store.id,
                    license_number=ret["license_number"],
                    license_type="CL_2",
                    issuing_authority="Karnataka Excise Department",
                    jurisdiction=ret["jurisdiction"],
                    valid_from=date(2026, 1, 1),
                    valid_until=date(2026, 12, 31),
                    status="ACTIVE",
                )
                session.add(lic)
                print(f"  Retailer seeded: {ret['trade_name']} ({ret['store_code']})")

    print("\n[OK] Seeded retailer organizations, stores, and excise licenses.")


if __name__ == "__main__":
    asyncio.run(seed())
