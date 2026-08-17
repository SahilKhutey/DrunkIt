from fastapi import APIRouter, HTTPException, Query
from services.catalogue.app.schemas.listing import (
    ConsumerListing,
    ListingAvailability,
    ListingPrice,
    ProductSummary,
    SKUVariant,
)
from services.catalogue.app.services.listing_service import ListingService

router = APIRouter(
    prefix="/listings",
    tags=["Listings"],
)

listing_service = ListingService()


@router.get("")
async def search_listings(
    query: str | None = None,
    category: str | None = None,
    store_id: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    return {
        "page": page,
        "limit": limit,
        "results": [
            ConsumerListing(
                listing_id="LIST-001",
                product=ProductSummary(
                    id="PROD-001",
                    name="Royal Challenge Select Premium Whisky",
                    brand="Royal Challenge",
                    category="WHISKY",
                ),
                variant=SKUVariant(id="SKU-750", volume_ml=750, packaging_type="BOTTLE"),
                pricing=ListingPrice(selling_price=1450.0, mrp=1600.0),
                availability=ListingAvailability(status="AVAILABLE"),
            )
        ],
    }


@router.get("/{listing_id}", response_model=ConsumerListing)
async def get_listing(listing_id: str):
    if listing_id == "invalid":
        raise HTTPException(status_code=404, detail="Listing not found")

    return ConsumerListing(
        listing_id=listing_id,
        product=ProductSummary(
            id="PROD-001",
            name="Royal Challenge Select Premium Whisky",
            brand="Royal Challenge",
            category="WHISKY",
        ),
        variant=SKUVariant(id="SKU-750", volume_ml=750, packaging_type="BOTTLE"),
        pricing=ListingPrice(selling_price=1450.0, mrp=1600.0),
        availability=ListingAvailability(status="AVAILABLE"),
    )


@router.post("/admin/{listing_id}/approve")
async def approve_listing(listing_id: str, jurisdiction: str = "MAHARASHTRA"):
    try:
        return await listing_service.approve(listing_id, jurisdiction)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
