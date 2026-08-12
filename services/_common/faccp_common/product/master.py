"""
Product Master (Authoritative Truth Layer).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, IntEnum
from typing import Any, ClassVar


class ProductLifecycleState(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VALIDATING = "VALIDATING"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class VisibilityLevel(IntEnum):
    PUBLIC = 0
    AUTHENTICATED = 1
    VERIFIED = 2
    TRANSACTION_ELIGIBLE = 3
    RETAILER = 4
    ADMINISTRATIVE = 5
    INTERNAL_SYSTEM = 6


@dataclass
class SKU:
    sku_id: str
    product_id: str
    code: str
    volume_ml: int
    packaging: str = "bottle"


@dataclass
class ProductMaster:
    product_id: str
    brand_id: str
    name: str
    category_id: str
    description: str
    manufacturer: str
    attributes: dict[str, Any] = field(default_factory=dict)
    compliance_metadata: dict[str, Any] = field(default_factory=dict)
    state: ProductLifecycleState = ProductLifecycleState.DRAFT
    version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    CATALOG_MODULES: ClassVar[list[str]] = [
        "Product Master",
        "Product Classification",
        "Product Attributes",
        "Product Media",
        "Product Compliance",
        "Brand Catalog",
        "Category Catalog",
        "SKU Catalog",
        "Variant Catalog",
        "Retailer Catalog",
        "Store Availability",
        "Pricing Integration",
        "Inventory Integration",
        "Search Index",
        "Product Documents",
        "Product Versioning",
    ]
