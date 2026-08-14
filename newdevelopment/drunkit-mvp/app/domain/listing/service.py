from __future__ import annotations

import math

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import models
from app.domain.eligibility.engine import evaluate_eligibility
from app.domain.listing.composer import ConsumerListingView, compose_listing

settings = get_settings()


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def get_nearby_listings(
    db: Session,
    *,
    latitude: float,
    longitude: float,
    state_key: str,
    consumer: models.Consumer | None,
    max_distance_km: float = 8.0,
    category: str | None = None,
) -> list[ConsumerListingView]:
    """
    Serviceability -> Store selection -> Listing composition, in that
    order. A store outside max_distance_km or in a non-serviceable
    state simply never enters the candidate set.
    """
    eligibility = evaluate_eligibility(
        state_key=state_key,
        date_of_birth=consumer.date_of_birth.date() if consumer and consumer.date_of_birth else None,
    )

    stores = (
        db.query(models.Store)
        .filter(models.Store.active.is_(True), models.Store.is_open.is_(True))
        .filter(models.Store.state == state_key.strip().upper().replace(" ", "_"))
        .all()
    )

    nearby_stores = [
        s for s in stores if _haversine_km(latitude, longitude, s.latitude, s.longitude) <= max_distance_km
    ]
    if not nearby_stores:
        return []

    store_ids = [s.id for s in nearby_stores]
    stores_by_id = {s.id: s for s in nearby_stores}

    query = (
        db.query(models.Listing)
        .filter(models.Listing.store_id.in_(store_ids))
        .filter(models.Listing.status == models.ListingStatus.ACTIVE)
    )
    listings = query.all()

    results: list[ConsumerListingView] = []
    for listing in listings:
        product = listing.product
        if not product.active:
            continue
        if category and product.category != category:
            continue

        store = stores_by_id[listing.store_id]
        retailer = store.retailer

        inventory = (
            db.query(models.InventoryItem)
            .filter_by(store_id=store.id, product_id=product.id)
            .first()
        )
        price = (
            db.query(models.PriceRecord)
            .filter_by(store_id=store.id, product_id=product.id)
            .first()
        )

        view = compose_listing(
            listing=listing,
            product=product,
            inventory=inventory,
            price=price,
            store=store,
            retailer=retailer,
            eligibility=eligibility,
            eta_min=settings.default_eta_min_minutes,
            eta_max=settings.default_eta_max_minutes,
        )
        if view is not None:
            results.append(view)

    return results


def get_listing_by_id(db: Session, *, listing_id: str, consumer: models.Consumer | None) -> ConsumerListingView | None:
    listing = db.query(models.Listing).filter_by(id=listing_id).first()
    if listing is None:
        return None

    product = listing.product
    store = listing.store
    retailer = store.retailer

    inventory = db.query(models.InventoryItem).filter_by(store_id=store.id, product_id=product.id).first()
    price = db.query(models.PriceRecord).filter_by(store_id=store.id, product_id=product.id).first()

    eligibility = evaluate_eligibility(
        state_key=consumer.state if consumer else store.state,
        date_of_birth=consumer.date_of_birth.date() if consumer and consumer.date_of_birth else None,
    )

    return compose_listing(
        listing=listing,
        product=product,
        inventory=inventory,
        price=price,
        store=store,
        retailer=retailer,
        eligibility=eligibility,
        eta_min=settings.default_eta_min_minutes,
        eta_max=settings.default_eta_max_minutes,
    )
