"""
Listing Engine (MVP slice).

Composes a ConsumerListingView from Product + Inventory + Price +
Listing status + Eligibility, WITHOUT copying those tables into a
single "listing" row. This is the same separation from the original
architecture doc, just without the template registry / field-resolver
machinery — one hardcoded card shape is enough until there's a second
consumer segment that actually needs a different one.

Fail-closed rule: if inventory or price data is missing for a listing,
we do not guess. The listing is simply not returned in results.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db import models
from app.domain.eligibility.engine import EligibilityResult


@dataclass(frozen=True)
class ConsumerListingView:
    listing_id: str
    product_id: str
    name: str
    brand: str
    category: str
    variant: str | None
    pack_size: str
    image_url: str | None

    mrp_paise: int
    selling_price_paise: int
    discount_percentage: float

    availability_status: str  # InventoryStatus value

    store_id: str
    store_name: str
    eta_min_minutes: int
    eta_max_minutes: int

    seller_verified: bool

    can_view: bool
    can_add_to_cart: bool
    eligibility_reason: str


def compose_listing(
    *,
    listing: models.Listing,
    product: models.Product,
    inventory: models.InventoryItem | None,
    price: models.PriceRecord | None,
    store: models.Store,
    retailer: models.Retailer,
    eligibility: EligibilityResult,
    eta_min: int,
    eta_max: int,
) -> ConsumerListingView | None:
    # Fail closed: no price or no inventory record → don't show it.
    # Never invent a price or assume in-stock.
    if price is None or inventory is None:
        return None

    if listing.status != models.ListingStatus.ACTIVE:
        return None

    return ConsumerListingView(
        listing_id=listing.id,
        product_id=product.id,
        name=product.name,
        brand=product.brand,
        category=product.category,
        variant=product.variant,
        pack_size=product.pack_size,
        image_url=product.image_url,
        mrp_paise=price.mrp_paise,
        selling_price_paise=price.selling_price_paise,
        discount_percentage=price.discount_percentage,
        availability_status=inventory.status.value,
        store_id=store.id,
        store_name=store.name,
        eta_min_minutes=eta_min,
        eta_max_minutes=eta_max,
        seller_verified=retailer.verified,
        can_view=eligibility.can_view,
        can_add_to_cart=eligibility.can_add_to_cart and inventory.status.value != "OUT_OF_STOCK",
        eligibility_reason=eligibility.reason,
    )
