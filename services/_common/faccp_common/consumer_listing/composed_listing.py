"""
Composed Consumer Listing View Object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class VisualIdentity:
    product_image_url: str
    brand_name: str
    product_name: str


@dataclass
class ProductIdentity:
    product_id: str
    variant_name: str
    pack_size: str


@dataclass
class CommercialDetails:
    mrp: float
    selling_price: float
    discount_percentage: float


@dataclass
class TrustDetails:
    seller_verified: bool = True
    listing_verified: bool = True
    license_status: str = "VERIFIED"


@dataclass
class ConsumerListingView:
    visual: VisualIdentity
    identity: ProductIdentity
    commercial: CommercialDetails
    availability_status: str
    store_name: str
    eta_minutes: str
    trust: TrustDetails
    actions: dict[str, bool] = field(default_factory=dict)

    ENGINE_MODULES: ClassVar[list[str]] = [
        "ProductCard",
        "ProductGrid",
        "SearchResultCard",
        "CategoryListing",
        "ProductDetail",
        "PriceDisplay",
        "AvailabilityBadge",
        "SellerVerificationBadge",
        "EligibilityBanner",
        "StoreAvailability",
        "DeliveryETA",
        "RecommendationCarousel",
        "ListingTemplateRenderer",
        "ResponsiveLayout",
        "LoadingSkeletonStates",
        "EmptyErrorStates",
        "AccessibilityLayer",
        "AnalyticsEvents",
    ]
