"""Master catalog domain models for brands, products, variants, and taste profiles."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Brand(Base):
    """Canonical brand entity."""

    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="brand",
        cascade="all, delete-orphan",
    )


class Category(Base):
    """Hierarchical category definition (e.g. Spirits -> Single Malt Whisky)."""

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Relationships
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
    )
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
    )


class Product(Base):
    """Canonical alcohol product."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("brands.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_type: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country_of_origin: Mapped[str | None] = mapped_column(String(2), nullable=True)
    abv: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    category: Mapped["Category | None"] = relationship("Category", back_populates="products")
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    attributes: Mapped[list["ProductAttribute"]] = relationship(
        "ProductAttribute",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    taste_profile: Mapped["TasteProfile | None"] = relationship(
        "TasteProfile",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ProductVariant(Base):
    """Specific volume and packaging format for a canonical product."""

    __tablename__ = "product_variants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    volume_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    packaging_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    package_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")

    __table_args__ = (
        CheckConstraint("volume_ml > 0", name="chk_variant_volume_positive"),
        CheckConstraint("package_count > 0", name="chk_variant_package_count_positive"),
        UniqueConstraint(
            "product_id",
            "volume_ml",
            "packaging_type",
            "package_count",
            name="uq_product_variant_specs",
        ),
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    skus: Mapped[list["SKU"]] = relationship(
        "SKU",
        back_populates="variant",
        cascade="all, delete-orphan",
    )


class SKU(Base):
    """Universal canonical barcode / stock keeping unit."""

    __tablename__ = "skus"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
    )
    canonical_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")

    # Relationships
    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="skus")


class ProductAttribute(Base):
    """Dynamic key-value attributes for search and filtering."""

    __tablename__ = "product_attributes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("idx_product_attributes_key_value", "key", "value"),
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="attributes")


class TasteProfile(Base):
    """Structured taste metrics for flavor radar and recommendation matching."""

    __tablename__ = "taste_profiles"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    )
    body: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    sweetness: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    smokiness: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    bitterness: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    fruitiness: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    spiciness: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="taste_profile")
