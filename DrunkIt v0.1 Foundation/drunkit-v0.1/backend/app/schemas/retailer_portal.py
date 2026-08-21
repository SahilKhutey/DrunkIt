"""Pydantic schemas for Retailer Portal, Bulk POS Feeds, and Store Order Operations."""

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.commerce import OrderResponse


class BulkInventoryFeedItem(BaseModel):
    """Line item in a bulk POS inventory feed upload."""

    external_sku: str = Field(min_length=1, max_length=100, description="Bar-code or POS SKU identifier")
    quantity: int = Field(ge=0, description="Current physical store stock count")
    price_minor: int | None = Field(default=None, ge=0, description="Statutory MRP/price in paise (₹4,200 = 420000)")


class BulkInventoryFeedRequest(BaseModel):
    """Payload for bulk POS inventory sync or CSV upload."""

    source: str = Field(default="POS_SYNC", description="POS_SYNC, CSV_UPLOAD, REST_FEED, MANUAL")
    items: list[BulkInventoryFeedItem] = Field(min_length=1)


class BulkInventoryFeedResponse(BaseModel):
    """Summary result of a bulk inventory ingestion job."""

    total_items: int
    mapped_count: int
    unmapped_count: int
    unmapped_skus: list[str] = Field(default_factory=list)
    snapshots_created: int
    prices_updated: int


class RetailerStoreOrdersResponse(BaseModel):
    """Order fulfillment queue for a store location."""

    location_id: uuid.UUID
    location_name: str
    orders: list[OrderResponse] = Field(default_factory=list)
    total_orders: int
    pending_fulfillment_count: int


class RetailerStoreDashboardResponse(BaseModel):
    """Real-time store dashboard analytics and inventory health."""

    location_id: uuid.UUID
    location_name: str
    active_skus_count: int
    in_stock_skus_count: int
    low_stock_skus_count: int
    out_of_stock_skus_count: int
    total_orders_count: int
    total_gmv_minor: int
    total_gmv_formatted: str
