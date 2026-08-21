"""Catalog API endpoints for Products, Brands, Categories, and Taste Profiles."""

import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.exceptions import ResourceNotFoundError
from app.db.session import get_sync_db
from app.db.uow import SyncUnitOfWork
from app.models.identity import User
from app.schemas.catalog import (
    BrandCreate,
    BrandResponse,
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductSummaryResponse,
)
from app.services.catalog_service import CatalogService

router = APIRouter(tags=["catalog"])


# ──────────────────────────────────────────────────────────────────────────────
# 1. Product Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/products",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    summary="List and search canonical products",
)
def list_products(
    q: str | None = Query(default=None, description="Search by name, description, or region"),
    category_id: uuid.UUID | None = Query(default=None, description="Filter by category UUID"),
    brand_id: uuid.UUID | None = Query(default=None, description="Filter by brand UUID"),
    product_type: str | None = Query(default=None, description="WHISKY, GIN, VODKA, TEQUILA, RUM, RTD"),
    min_abv: Decimal | None = Query(default=None, ge=0, le=100),
    max_abv: Decimal | None = Query(default=None, ge=0, le=100),
    region: str | None = Query(default=None, description="Origin region (e.g. Haryana, Goa, Scotland)"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_sync_db),
) -> ProductListResponse:
    """Search and browse canonical products with multi-attribute filtering."""
    items, total = CatalogService.list_products(
        q=q,
        category_id=category_id,
        brand_id=brand_id,
        product_type=product_type,
        min_abv=min_abv,
        max_abv=max_abv,
        region=region,
        limit=limit,
        offset=offset,
        session=session,
    )

    summaries = [
        ProductSummaryResponse(
            id=p.id,
            brand_id=p.brand_id,
            brand_name=p.brand.name if p.brand else None,
            category_id=p.category_id,
            category_name=p.category.name if p.category else None,
            name=p.name,
            slug=p.slug,
            product_type=p.product_type,
            region=p.region,
            country_of_origin=p.country_of_origin,
            abv=p.abv,
            status=p.status,
            created_at=p.created_at,
        )
        for p in items
    ]

    return ProductListResponse(
        items=summaries,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/products/{product_id}",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get canonical product details",
)
def get_product(
    product_id: str,
    session: Session = Depends(get_sync_db),
) -> ProductDetailResponse:
    """Retrieve full product detail including brand story, variants, SKUs, and taste profile."""
    product = CatalogService.get_product(product_id, session)
    if not product:
        raise ResourceNotFoundError(f"Product '{product_id}' was not found.")

    return ProductDetailResponse(
        id=product.id,
        brand_id=product.brand_id,
        brand_name=product.brand.name if product.brand else None,
        category_id=product.category_id,
        category_name=product.category.name if product.category else None,
        name=product.name,
        slug=product.slug,
        description=product.description,
        product_type=product.product_type,
        region=product.region,
        country_of_origin=product.country_of_origin,
        abv=product.abv,
        status=product.status,
        created_at=product.created_at,
        brand=BrandResponse.model_validate(product.brand) if product.brand else None,
        category=CategoryResponse.model_validate(product.category) if product.category else None,
        variants=[v for v in product.variants],  # type: ignore[arg-type]
        attributes=[a for a in product.attributes],  # type: ignore[arg-type]
        taste_profile=product.taste_profile,  # type: ignore[arg-type]
    )


@router.post(
    "/products",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new canonical product (Admin/Brand only)",
)
def create_product(
    request: ProductCreate,
    current_user: User = Depends(require_roles("ADMIN", "BRAND")),
    session: Session = Depends(get_sync_db),
) -> ProductDetailResponse:
    """Create a canonical product with variants, SKUs, and taste attributes."""
    uow = SyncUnitOfWork(session)
    with uow:
        product = CatalogService.create_product(
            data=request,
            uow=uow,
            actor_id=current_user.id,
        )

    fresh = CatalogService.get_product(product.id, session) or product
    return get_product(str(fresh.id), session)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Brand Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/brands",
    response_model=list[BrandResponse],
    status_code=status.HTTP_200_OK,
    summary="List all master brand houses",
)
def list_brands(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_sync_db),
) -> list[BrandResponse]:
    """List active alcohol brands and distilleries."""
    brands = CatalogService.list_brands(limit=limit, offset=offset, session=session)
    return [BrandResponse.model_validate(b) for b in brands]


@router.get(
    "/brands/{brand_id}",
    response_model=BrandResponse,
    status_code=status.HTTP_200_OK,
    summary="Get brand profile",
)
def get_brand(
    brand_id: str,
    session: Session = Depends(get_sync_db),
) -> BrandResponse:
    """Retrieve brand profile by UUID or unique slug."""
    brand = CatalogService.get_brand(brand_id, session)
    if not brand:
        raise ResourceNotFoundError(f"Brand '{brand_id}' was not found.")
    return BrandResponse.model_validate(brand)


@router.get(
    "/brands/{brand_id}/products",
    response_model=list[ProductSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="List all products for a brand",
)
def get_brand_products(
    brand_id: str,
    session: Session = Depends(get_sync_db),
) -> list[ProductSummaryResponse]:
    """Retrieve canonical catalogue for a specific brand."""
    brand = CatalogService.get_brand(brand_id, session)
    if not brand:
        raise ResourceNotFoundError(f"Brand '{brand_id}' was not found.")

    items, _ = CatalogService.list_products(brand_id=brand.id, session=session)
    return [
        ProductSummaryResponse(
            id=p.id,
            brand_id=p.brand_id,
            brand_name=brand.name,
            category_id=p.category_id,
            category_name=p.category.name if p.category else None,
            name=p.name,
            slug=p.slug,
            product_type=p.product_type,
            region=p.region,
            country_of_origin=p.country_of_origin,
            abv=p.abv,
            status=p.status,
            created_at=p.created_at,
        )
        for p in items
    ]


@router.post(
    "/brands",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new brand (Admin/Brand only)",
)
def create_brand(
    request: BrandCreate,
    current_user: User = Depends(require_roles("ADMIN", "BRAND")),
    session: Session = Depends(get_sync_db),
) -> BrandResponse:
    """Register a new brand or distillery house."""
    uow = SyncUnitOfWork(session)
    with uow:
        brand = CatalogService.create_brand(
            data=request,
            uow=uow,
            actor_id=current_user.id,
        )
    return BrandResponse.model_validate(brand)


# ──────────────────────────────────────────────────────────────────────────────
# 3. Category Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List category hierarchy",
)
def list_categories(session: Session = Depends(get_sync_db)) -> list[CategoryResponse]:
    """Retrieve the master category hierarchy tree."""
    categories = CatalogService.list_categories(session)
    return [CategoryResponse.model_validate(c) for c in categories]


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category (Admin only)",
)
def create_category(
    request: CategoryCreate,
    current_user: User = Depends(require_roles("ADMIN")),
    session: Session = Depends(get_sync_db),
) -> CategoryResponse:
    """Create a new category node in the master taxonomy."""
    category = CatalogService.create_category(request, session)
    session.commit()
    return CategoryResponse.model_validate(category)
