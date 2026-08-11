"""Seed sample catalog data."""

import asyncio
from decimal import Decimal
from faccp_common.database import init_engine, session_scope
from app.config import get_settings
from app.schemas.catalog import CreateBrandRequest, CreateCategoryRequest, CreateProductRequest
from app.services.catalog_service import CatalogService

CATEGORIES = [
    ("beer", "Beer", 1),
    ("wine", "Wine", 2),
    ("spirit", "Spirits", 3),
    ("rtd", "Ready-to-Drink", 4),
]

BRANDS = [
    ("Kingfisher", "India"),
    ("Bira 91", "India"),
    ("Sula", "India"),
    ("Johnnie Walker", "Scotland"),
    ("Bacardi", "Cuba"),
]

PRODUCTS = [
    ("KF-650", "Kingfisher Premium Lager 650ml", "beer", 4.8, 650, 180.00),
    ("BIRA-WL-330", "Bira 91 White Ale 330ml", "beer", 4.7, 330, 120.00),
    ("SULA-CHEN-750", "Sula Chenin Blanc 750ml", "wine", 13.0, 750, 850.00),
    ("JW-RD-750", "Johnnie Walker Red Label 750ml", "spirit", 40.0, 750, 1800.00),
    ("BAC-WH-750", "Bacardi White Rum 750ml", "spirit", 37.5, 750, 1100.00),
    ("RTD-COLA-330", "Premium Whisky Cola RTD 330ml", "rtd", 5.0, 330, 150.00),
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        svc = CatalogService(db=session)
        cats = {}
        for code, name, order in CATEGORIES:
            c = await svc.create_category(CreateCategoryRequest(code=code, name=name, sort_order=order))
            cats[code] = c.id
        brands = {}
        for name, country in BRANDS:
            b = await svc.create_brand(CreateBrandRequest(name=name, country_of_origin=country))
            brands[name] = b.id
        for sku, name, cat, abv, vol, price in PRODUCTS:
            await svc.create_product(CreateProductRequest(
                sku=sku, name=name, category_id=cats[cat], brand_id=None,
                category=cat, abv=abv, volume_ml=vol, base_price=Decimal(str(price)),
            ))
    print(f"[OK] Seeded {len(CATEGORIES)} categories, {len(BRANDS)} brands, {len(PRODUCTS)} products")


if __name__ == "__main__":
    asyncio.run(seed())
