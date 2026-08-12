"""
Listing Template Renderer & Config Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar
from .composed_listing import ConsumerListingView


class ListingTemplateType(str, Enum):
    COMPACT_CARD = "COMPACT_CARD"
    RICH_CARD = "RICH_CARD"
    REGULATED_CARD = "REGULATED_CARD"


@dataclass
class TemplateConfig:
    template_id: str
    template_type: ListingTemplateType
    version: int = 1
    components: list[str] = field(default_factory=list)


class ListingTemplateRenderer:
    TEMPLATE_TYPES: ClassVar[list[ListingTemplateType]] = list(ListingTemplateType)

    def render(self, listing: ConsumerListingView, template_type: ListingTemplateType) -> dict[str, Any]:
        base = {
            "template_type": template_type.value,
            "product_name": listing.visual.product_name,
            "price": listing.commercial.selling_price,
            "availability": listing.availability_status,
        }
        if template_type == ListingTemplateType.RICH_CARD:
            base["mrp"] = listing.commercial.mrp
            base["discount"] = listing.commercial.discount_percentage
            base["eta"] = listing.eta_minutes
        elif template_type == ListingTemplateType.REGULATED_CARD:
            base["mrp"] = listing.commercial.mrp
            base["seller_verified"] = listing.trust.seller_verified
            base["listing_verified"] = listing.trust.listing_verified
            base["license_status"] = listing.trust.license_status
        return base
