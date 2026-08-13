"""Seed sample tenant branding and domain bindings."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import CustomDomainBinding, TenantBrandingConfig
from faccp_common.database import init_engine, session_scope

SAMPLE_BRANDING = [
    {
        "tenant_id": "tenant_royal_wines_blr",
        "brand_name": "Royal Spirits Bengaluru",
        "logo_url": "https://cdn.drunkit.io/tenants/royal_wines/logo.png",
        "primary_color_hex": "#1a202c",
        "secondary_color_hex": "#d69e2e",
    }
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for b in SAMPLE_BRANDING:
            existing = await session.execute(
                select(TenantBrandingConfig).where(TenantBrandingConfig.tenant_id == b["tenant_id"])
            )
            if existing.scalar_one_or_none() is None:
                brand = TenantBrandingConfig(
                    tenant_id=b["tenant_id"],
                    brand_name=b["brand_name"],
                    logo_url=b["logo_url"],
                    primary_color_hex=b["primary_color_hex"],
                    secondary_color_hex=b["secondary_color_hex"],
                )
                session.add(brand)
                print(f"  Whitelabel branding seeded: {b['brand_name']} ({b['tenant_id']})")

        dom = CustomDomainBinding(
            tenant_id="tenant_royal_wines_blr",
            domain_name="order.royalspirits.in",
            ssl_certified=True,
            status="ACTIVE",
        )
        session.add(dom)

    print("\n[OK] Seeded whitelabel tenant branding and domains.")


if __name__ == "__main__":
    asyncio.run(seed())
