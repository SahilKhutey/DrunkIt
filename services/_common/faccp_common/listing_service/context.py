"""
Listing Context & DTO Definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar


class ListingStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    READY = "READY"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class InventoryStatus(str, Enum):
    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    UNKNOWN = "UNKNOWN"


@dataclass
class ListingContext:
    product_id: str
    sku_id: str
    retailer_id: str
    store_id: str
    product_data: dict[str, Any] = field(default_factory=dict)
    retailer_data: dict[str, Any] = field(default_factory=dict)
    inventory_state: InventoryStatus = InventoryStatus.IN_STOCK
    pricing_state: dict[str, Any] = field(default_factory=dict)
    fulfilment_state: dict[str, Any] = field(default_factory=dict)
    policy_state: dict[str, Any] = field(default_factory=dict)
    user_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProductCardView:
    listing_id: str
    product_id: str
    name: str
    brand: str
    selling_price: float
    availability: InventoryStatus
    actions: dict[str, bool]


@dataclass
class ProductDetailView:
    card: ProductCardView
    description: str
    attributes: list[dict[str, Any]]
    store_name: str
    trust_badges: list[str]

    CORE_MODULES: ClassVar[list[str]] = [
        "catalog",
        "listings",
        "templates",
        "rendering",
        "availability",
        "pricing",
        "fulfilment",
        "eligibility",
        "actions",
        "ranking",
        "search",
        "personalization",
        "caching",
        "events",
        "analytics",
        "validation",
        "audit",
    ]

    TEMPLATE_TYPES: ClassVar[list[str]] = [
        "CARD",
        "GRID_CARD",
        "LIST_CARD",
        "SEARCH_RESULT",
        "PRODUCT_DETAIL",
        "CATEGORY_RESULT",
        "STORE_PRODUCT",
        "RECOMMENDATION_CARD",
    ]
