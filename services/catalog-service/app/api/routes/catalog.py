"""Catalog API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_catalog_service
from app.schemas.catalog import (
    BrandCreate, BrandResponse, CategoryCreate, CategoryResponse,
    ProductCreate, ProductResponse, StoreListingCreate, StoreListingResponse,
)
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/catalog", tags=["Catalog Engine"])


@router.post("/categories", response_model=SuccessResponse[CategoryResponse], status_code=201)
async def create_category(
    payload: CategoryCreate,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[CategoryResponse]:
    cat = await service.create_category(payload)
    return SuccessResponse(data=CategoryResponse(
        id=cat.id, code=cat.code, name=cat.name, description=cat.description,
        parent_id=cat.parent_id, is_active=cat.is_active,
    ), message="Category created")


@router.get("/categories", response_model=SuccessResponse[list[CategoryResponse]])
async def list_categories(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[list[CategoryResponse]]:
    cats = await service.list_categories()
    return SuccessResponse(data=[CategoryResponse(
        id=c.id, code=c.code, name=c.name, description=c.description,
        parent_id=c.parent_id, is_active=c.is_active,
    ) for c in cats])


@router.post("/brands", response_model=SuccessResponse[BrandResponse], status_code=201)
async def create_brand(
    payload: BrandCreate,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[BrandResponse]:
    brand = await service.create_brand(payload)
    return SuccessResponse(data=BrandResponse(
        id=brand.id, code=brand.code, name=brand.name,
        manufacturer=brand.manufacturer, origin_country=brand.origin_country,
        is_active=brand.is_active,
    ), message="Brand created")


@router.get("/brands", response_model=SuccessResponse[list[BrandResponse]])
async def list_brands(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[list[BrandResponse]]:
    brands = await service.list_brands()
    return SuccessResponse(data=[BrandResponse(
        id=b.id, code=b.code, name=b.name, manufacturer=b.manufacturer,
        origin_country=b.origin_country, is_active=b.is_active,
    ) for b in brands])


@router.post("/products", response_model=SuccessResponse[ProductResponse], status_code=201)
async def create_product(
    payload: ProductCreate,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[ProductResponse]:
    product = await service.create_product(payload)
    return SuccessResponse(data=ProductResponse(
        id=product.id, gtin=product.gtin, title=product.title,
        brand_id=product.brand_id, category_id=product.category_id,
        volume_ml=product.volume_ml, abv_percentage=product.abv_percentage,
        packaging_type=product.packaging_type, image_url=product.image_url,
        description=product.description, is_active=product.is_active,
    ), message="Product Master created")


@router.get("/products/{product_id}", response_model=SuccessResponse[ProductResponse])
async def get_product(
    product_id: str,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[ProductResponse]:
    p = await service.get_product(product_id)
    return SuccessResponse(data=ProductResponse(
        id=p.id, gtin=p.gtin, title=p.title, brand_id=p.brand_id,
        category_id=p.category_id, volume_ml=p.volume_ml, abv_percentage=p.abv_percentage,
        packaging_type=p.packaging_type, image_url=p.image_url, description=p.description,
        is_active=p.is_active,
    ))


@router.get("/products", response_model=SuccessResponse[list[ProductResponse]])
async def list_products(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[list[ProductResponse]]:
    products = await service.list_products()
    return SuccessResponse(data=[ProductResponse(
        id=p.id, gtin=p.gtin, title=p.title, brand_id=p.brand_id,
        category_id=p.category_id, volume_ml=p.volume_ml, abv_percentage=p.abv_percentage,
        packaging_type=p.packaging_type, image_url=p.image_url, description=p.description,
        is_active=p.is_active,
    ) for p in products])


@router.post("/store-listings", response_model=SuccessResponse[StoreListingResponse], status_code=201)
async def create_store_listing(
    payload: StoreListingCreate,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[StoreListingResponse]:
    listing = await service.create_store_listing(payload)
    return SuccessResponse(data=StoreListingResponse(
        id=listing.id, store_id=listing.store_id, sku_id=listing.sku_id,
        mrp_inr=listing.mrp_inr, selling_price_inr=listing.selling_price_inr,
        is_available=listing.is_available,
    ), message="Store listing created")


@router.get("/store-listings/{store_id}", response_model=SuccessResponse[list[StoreListingResponse]])
async def list_store_listings(
    store_id: str,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SuccessResponse[list[StoreListingResponse]]:
    listings = await service.list_store_listings(store_id)
    return SuccessResponse(data=[StoreListingResponse(
        id=l.id, store_id=l.store_id, sku_id=l.sku_id, mrp_inr=l.mrp_inr,
        selling_price_inr=l.selling_price_inr, is_available=l.is_available,
    ) for l in listings])
