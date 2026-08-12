"""Catalog service: Product Master, Categories, Brands, SKUs, Store Listings."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.exceptions import ConflictError, NotFoundError
from faccp_common.logging import get_logger

from app.db.models import Brand, Category, ProductMaster, SKU, StoreListing
from app.schemas.catalog import (
    BrandCreate, CategoryCreate, ProductCreate, StoreListingCreate,
)

logger = get_logger(__name__)


class CatalogService:
    """Canonical catalog and product master orchestrator."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    # ============================================================
    # CATEGORY MANAGEMENT
    # ============================================================
    async def create_category(self, payload: CategoryCreate) -> Category:
        existing = await self._get_category_by_code(payload.code)
        if existing:
            raise ConflictError(f"Category code {payload.code} already exists")

        cat = Category(
            code=payload.code,
            name=payload.name,
            description=payload.description,
            parent_id=payload.parent_id,
            is_active=True,
        )
        self.db.add(cat)
        await self.db.commit()
        await self.db.refresh(cat)
        return cat

    async def list_categories(self) -> list[Category]:
        result = await self.db.execute(select(Category).where(Category.is_active == True))  # noqa: E712
        return list(result.scalars().all())

    # ============================================================
    # BRAND MANAGEMENT
    # ============================================================
    async def create_brand(self, payload: BrandCreate) -> Brand:
        existing = await self._get_brand_by_code(payload.code)
        if existing:
            raise ConflictError(f"Brand code {payload.code} already exists")

        brand = Brand(
            code=payload.code,
            name=payload.name,
            manufacturer=payload.manufacturer,
            origin_country=payload.origin_country,
            is_active=True,
        )
        self.db.add(brand)
        await self.db.commit()
        await self.db.refresh(brand)
        return brand

    async def list_brands(self) -> list[Brand]:
        result = await self.db.execute(select(Brand).where(Brand.is_active == True))  # noqa: E712
        return list(result.scalars().all())

    # ============================================================
    # PRODUCT MASTER MANAGEMENT
    # ============================================================
    async def create_product(self, payload: ProductCreate) -> ProductMaster:
        existing = await self._get_product_by_gtin(payload.gtin)
        if existing:
            raise ConflictError(f"Product GTIN {payload.gtin} already exists")

        product = ProductMaster(
            gtin=payload.gtin,
            title=payload.title,
            brand_id=payload.brand_id,
            category_id=payload.category_id,
            volume_ml=payload.volume_ml,
            abv_percentage=payload.abv_percentage,
            packaging_type=payload.packaging_type,
            image_url=payload.image_url,
            description=payload.description,
            is_active=True,
        )
        self.db.add(product)
        await self.db.flush()

        # Auto-create default SKU under product
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU_{payload.gtin}",
            barcode=payload.gtin,
            pack_size=1,
            is_active=True,
        )
        self.db.add(sku)
        await self.db.commit()
        await self.db.refresh(product)

        await self._publish("catalog.product_created", {
            "product_id": product.id, "gtin": product.gtin, "title": product.title,
        })
        return product

    async def get_product(self, product_id: str) -> ProductMaster:
        result = await self.db.execute(select(ProductMaster).where(ProductMaster.id == product_id))
        p = result.scalar_one_or_none()
        if not p:
            raise NotFoundError(f"Product {product_id} not found")
        return p

    async def list_products(self) -> list[ProductMaster]:
        result = await self.db.execute(select(ProductMaster).where(ProductMaster.is_active == True))  # noqa: E712
        return list(result.scalars().all())

    # ============================================================
    # STORE LISTING MANAGEMENT
    # ============================================================
    async def create_store_listing(self, payload: StoreListingCreate) -> StoreListing:
        listing = StoreListing(
            store_id=payload.store_id,
            sku_id=payload.sku_id,
            mrp_inr=payload.mrp_inr,
            selling_price_inr=payload.selling_price_inr,
            is_available=payload.is_available,
        )
        self.db.add(listing)
        await self.db.commit()
        await self.db.refresh(listing)
        return listing

    async def list_store_listings(self, store_id: str) -> list[StoreListing]:
        result = await self.db.execute(
            select(StoreListing).where(StoreListing.store_id == store_id)
        )
        return list(result.scalars().all())

    # ============================================================
    # HELPERS
    # ============================================================
    async def _get_category_by_code(self, code: str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.code == code))
        return result.scalar_one_or_none()

    async def _get_brand_by_code(self, code: str) -> Brand | None:
        result = await self.db.execute(select(Brand).where(Brand.code == code))
        return result.scalar_one_or_none()

    async def _get_product_by_gtin(self, gtin: str) -> ProductMaster | None:
        result = await self.db.execute(select(ProductMaster).where(ProductMaster.gtin == gtin))
        return result.scalar_one_or_none()

    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-catalog")
            await self.producer.publish("catalog.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
