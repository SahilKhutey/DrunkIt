"""Seed sample catalog categories, brands, and product masters."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import Brand, Category, ProductMaster, SKU
from faccp_common.database import init_engine, session_scope

CATEGORIES = [
    {"code": "WHISKY", "name": "Whisky & Bourbon", "description": "Single malt, blended scotch, Indian whisky"},
    {"code": "BEER", "name": "Beer & Cider", "description": "Lager, ale, craft beer, cider"},
    {"code": "WINE", "name": "Wine & Champagne", "description": "Red wine, white wine, sparkling wine"},
    {"code": "VODKA", "name": "Vodka", "description": "Clear and flavored vodkas"},
    {"code": "GIN", "name": "Gin & Botanicals", "description": "London dry gin, craft gin"},
]

BRANDS = [
    {"code": "AMRUT", "name": "Amrut Single Malt", "manufacturer": "Amrut Distilleries", "origin_country": "IN"},
    {"code": "KINGFISHER", "name": "Kingfisher", "manufacturer": "United Breweries", "origin_country": "IN"},
    {"code": "SULA", "name": "Sula Vineyards", "manufacturer": "Sula Vineyards Ltd", "origin_country": "IN"},
]

PRODUCTS = [
    {
        "gtin": "8901234567890",
        "title": "Amrut Fusion Single Malt Indian Whisky 750ml",
        "brand_code": "AMRUT",
        "category_code": "WHISKY",
        "volume_ml": 750,
        "abv_percentage": 50.0,
        "packaging_type": "GLASS_BOTTLE",
    },
    {
        "gtin": "8901234567891",
        "title": "Kingfisher Premium Lager Beer 650ml",
        "brand_code": "KINGFISHER",
        "category_code": "BEER",
        "volume_ml": 650,
        "abv_percentage": 4.8,
        "packaging_type": "GLASS_BOTTLE",
    },
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        cat_map = {}
        for c in CATEGORIES:
            existing = await session.execute(select(Category).where(Category.code == c["code"]))
            cat = existing.scalar_one_or_none()
            if not cat:
                cat = Category(code=c["code"], name=c["name"], description=c["description"], is_active=True)
                session.add(cat)
                await session.flush()
            cat_map[c["code"]] = cat.id

        brand_map = {}
        for b in BRANDS:
            existing = await session.execute(select(Brand).where(Brand.code == b["code"]))
            brand = existing.scalar_one_or_none()
            if not brand:
                brand = Brand(code=b["code"], name=b["name"], manufacturer=b["manufacturer"], origin_country=b["origin_country"], is_active=True)
                session.add(brand)
                await session.flush()
            brand_map[b["code"]] = brand.id

        for p in PRODUCTS:
            existing = await session.execute(select(ProductMaster).where(ProductMaster.gtin == p["gtin"]))
            if existing.scalar_one_or_none() is None:
                prod = ProductMaster(
                    gtin=p["gtin"],
                    title=p["title"],
                    brand_id=brand_map[p["brand_code"]],
                    category_id=cat_map[p["category_code"]],
                    volume_ml=p["volume_ml"],
                    abv_percentage=p["abv_percentage"],
                    packaging_type=p["packaging_type"],
                    is_active=True,
                )
                session.add(prod)
                await session.flush()

                sku = SKU(
                    product_id=prod.id,
                    sku_code=f"SKU_{p['gtin']}",
                    barcode=p["gtin"],
                    pack_size=1,
                    is_active=True,
                )
                session.add(sku)
                print(f"  Product seeded: {p['title']} (GTIN {p['gtin']})")

    print("\n[OK] Seeded catalog categories, brands, and product masters.")


if __name__ == "__main__":
    asyncio.run(seed())
