"""Master catalog service for brands, categories, products, variants, and taste profiles."""

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ConflictError, ResourceNotFoundError
from app.db.uow import SyncUnitOfWork
from app.models.catalog import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductVariant,
    SKU,
    TasteProfile,
)
from app.schemas.catalog import (
    BrandCreate,
    CategoryCreate,
    ProductCreate,
)


class CatalogService:
    """Service managing master catalog data and queries."""

    # 1. Brand Management
    @classmethod
    def create_brand(
        cls,
        data: BrandCreate,
        uow: SyncUnitOfWork,
        actor_id: uuid.UUID | None = None,
    ) -> Brand:
        """Create a new master brand house."""
        session = uow.session
        existing = session.scalars(select(Brand).where(Brand.slug == data.slug)).first()
        if existing:
            raise ConflictError(f"A brand with slug '{data.slug}' already exists.")

        brand = Brand(
            name=data.name,
            slug=data.slug,
            description=data.description,
            country_code=data.country_code,
            status=data.status,
        )
        session.add(brand)
        session.flush()

        uow.record_audit(
            actor_id=actor_id,
            action="BRAND_CREATED",
            entity_type="Brand",
            entity_id=brand.id,
            metadata={"brand_name": brand.name, "slug": brand.slug},
        )
        uow.publish_outbox(
            event_type="BRAND_CREATED",
            aggregate_type="Brand",
            aggregate_id=brand.id,
            payload={"brand_id": str(brand.id), "slug": brand.slug, "name": brand.name},
        )
        return brand

    @staticmethod
    def get_brand(identifier: str | uuid.UUID, session: Session) -> Brand | None:
        """Fetch a brand by UUID or unique slug."""
        if isinstance(identifier, uuid.UUID):
            return session.get(Brand, identifier)
        try:
            parsed_uuid = uuid.UUID(identifier)
            return session.get(Brand, parsed_uuid)
        except ValueError:
            return session.scalars(select(Brand).where(Brand.slug == identifier)).first()

    @staticmethod
    def list_brands(
        limit: int = 50,
        offset: int = 0,
        session: Session = None,  # type: ignore[assignment]
    ) -> list[Brand]:
        """List active master brands."""
        return list(
            session.scalars(
                select(Brand)
                .where(Brand.status == "ACTIVE")
                .order_by(Brand.name.asc())
                .offset(offset)
                .limit(limit)
            ).all()
        )

    # 2. Category Management
    @staticmethod
    def create_category(data: CategoryCreate, session: Session) -> Category:
        """Create a master category."""
        existing = session.scalars(select(Category).where(Category.slug == data.slug)).first()
        if existing:
            raise ConflictError(f"A category with slug '{data.slug}' already exists.")

        category = Category(
            name=data.name,
            slug=data.slug,
            parent_id=data.parent_id,
        )
        session.add(category)
        session.flush()
        return category

    @staticmethod
    def list_categories(session: Session) -> list[Category]:
        """List root and child categories."""
        return list(
            session.scalars(
                select(Category)
                .options(selectinload(Category.children))
                .where(Category.parent_id.is_(None))
                .order_by(Category.name.asc())
            ).all()
        )

    # 3. Product & SKU Management
    @classmethod
    def create_product(
        cls,
        data: ProductCreate,
        uow: SyncUnitOfWork,
        actor_id: uuid.UUID | None = None,
    ) -> Product:
        """Create a canonical product with variants, SKUs, attributes, and taste profile."""
        session = uow.session

        # Validate brand exists
        brand = session.get(Brand, data.brand_id)
        if not brand:
            raise ResourceNotFoundError(f"Brand with id '{data.brand_id}' does not exist.")

        # Check duplicate product slug
        existing = session.scalars(select(Product).where(Product.slug == data.slug)).first()
        if existing:
            raise ConflictError(f"A product with slug '{data.slug}' already exists.")

        product = Product(
            brand_id=data.brand_id,
            category_id=data.category_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            product_type=data.product_type,
            region=data.region,
            country_of_origin=data.country_of_origin,
            abv=data.abv,
            status="ACTIVE",
        )
        session.add(product)
        session.flush()

        # Add Variants and SKUs
        for var_data in data.variants:
            variant = ProductVariant(
                product_id=product.id,
                volume_ml=var_data.volume_ml,
                packaging_type=var_data.packaging_type,
                package_count=var_data.package_count,
            )
            session.add(variant)
            session.flush()

            if var_data.sku:
                sku = SKU(
                    variant_id=variant.id,
                    canonical_code=var_data.sku.canonical_code,
                    barcode=var_data.sku.barcode,
                )
                session.add(sku)
            else:
                # Generate default canonical SKU code
                generated_code = f"SKU_{product.slug.upper().replace('-', '_')}_{var_data.volume_ml}"
                sku = SKU(variant_id=variant.id, canonical_code=generated_code)
                session.add(sku)

        # Add Attributes
        for attr_data in data.attributes:
            attr = ProductAttribute(
                product_id=product.id,
                key=attr_data.key,
                value=attr_data.value,
            )
            session.add(attr)

        # Add Taste Profile
        if data.taste_profile:
            taste = TasteProfile(
                product_id=product.id,
                body=data.taste_profile.body,
                sweetness=data.taste_profile.sweetness,
                smokiness=data.taste_profile.smokiness,
                bitterness=data.taste_profile.bitterness,
                fruitiness=data.taste_profile.fruitiness,
                spiciness=data.taste_profile.spiciness,
                confidence=data.taste_profile.confidence or Decimal("1.0"),
            )
            session.add(taste)

        session.flush()

        uow.record_audit(
            actor_id=actor_id,
            action="PRODUCT_CREATED",
            entity_type="Product",
            entity_id=product.id,
            metadata={"product_name": product.name, "slug": product.slug},
        )
        uow.publish_outbox(
            event_type="PRODUCT_CREATED",
            aggregate_type="Product",
            aggregate_id=product.id,
            payload={"product_id": str(product.id), "name": product.name, "slug": product.slug},
        )
        return product

    @staticmethod
    def get_product(identifier: str | uuid.UUID, session: Session) -> Product | None:
        """Fetch a rich canonical product with all related variants, SKUs, and taste profiles."""
        query = (
            select(Product)
            .options(
                selectinload(Product.brand),
                selectinload(Product.category),
                selectinload(Product.variants).selectinload(ProductVariant.skus),
                selectinload(Product.attributes),
                selectinload(Product.taste_profile),
            )
        )
        if isinstance(identifier, uuid.UUID):
            return session.scalars(query.where(Product.id == identifier)).first()
        try:
            parsed_uuid = uuid.UUID(identifier)
            return session.scalars(query.where(Product.id == parsed_uuid)).first()
        except ValueError:
            return session.scalars(query.where(Product.slug == identifier)).first()

    @staticmethod
    def list_products(
        q: str | None = None,
        category_id: uuid.UUID | None = None,
        brand_id: uuid.UUID | None = None,
        product_type: str | None = None,
        min_abv: Decimal | None = None,
        max_abv: Decimal | None = None,
        region: str | None = None,
        limit: int = 50,
        offset: int = 0,
        session: Session = None,  # type: ignore[assignment]
    ) -> tuple[list[Product], int]:
        """Query products with full-text search, multi-faceted filters, and pagination."""
        query = (
            select(Product)
            .options(selectinload(Product.brand), selectinload(Product.category))
            .where(Product.status == "ACTIVE")
        )

        if q:
            term = f"%{q.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Product.name).like(term),
                    func.lower(Product.description).like(term),
                    func.lower(Product.region).like(term),
                )
            )

        if category_id:
            query = query.where(Product.category_id == category_id)
        if brand_id:
            query = query.where(Product.brand_id == brand_id)
        if product_type:
            query = query.where(Product.product_type == product_type.upper())
        if min_abv is not None:
            query = query.where(Product.abv >= min_abv)
        if max_abv is not None:
            query = query.where(Product.abv <= max_abv)
        if region:
            query = query.where(func.lower(Product.region) == region.strip().lower())

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_count = session.scalar(count_query) or 0

        # Paginate
        paginated_query = query.order_by(Product.name.asc()).offset(offset).limit(limit)
        items = list(session.scalars(paginated_query).all())

        return items, total_count
