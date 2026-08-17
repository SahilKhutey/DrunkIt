from pydantic import BaseModel, Field


class ProductSummary(BaseModel):
    id: str
    name: str
    brand: str
    category: str


class SKUVariant(BaseModel):
    id: str
    volume_ml: int | None = None
    packaging_type: str | None = None


class ListingPrice(BaseModel):
    selling_price: float
    mrp: float | None = None


class ListingAvailability(BaseModel):
    status: str = "AVAILABLE"  # AVAILABLE, OUT_OF_STOCK, UNAVAILABLE, VERIFICATION_REQUIRED


class ConsumerListing(BaseModel):
    listing_id: str
    product: ProductSummary
    variant: SKUVariant
    pricing: ListingPrice
    availability: ListingAvailability
