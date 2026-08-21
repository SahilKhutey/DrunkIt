"""Pydantic schemas for Brand Portal, Regional Intelligence, and Taste Radar Visualizations."""

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BrandSKUMarketShare(BaseModel):
    """Performance breakdown for an individual brand SKU."""

    sku_id: uuid.UUID
    sku_code: str
    product_name: str
    volume_ml: int
    orders_count: int
    units_sold: int
    gross_revenue_minor: int
    gross_revenue_formatted: str

    model_config = ConfigDict(from_attributes=True)


class BrandRegionalDistribution(BaseModel):
    """Regional penetration and stockist density by state jurisdiction."""

    state_code: str
    state_name: str
    active_retailers_count: int
    active_locations_count: int
    in_stock_ratio: float
    volume_sold_litres: float

    model_config = ConfigDict(from_attributes=True)


class BrandTasteRadarVisualization(BaseModel):
    """6-axis flavor radar profile with peer category benchmarking."""

    product_id: uuid.UUID
    product_name: str
    product_slug: str
    radar_axes: dict[str, float] = Field(
        description="6-axis radar values: body, sweetness, smokiness, bitterness, fruitiness, spiciness (0.0 to 1.0)"
    )
    category_benchmark: dict[str, float] = Field(
        description="Average 6-axis flavor radar profile of peer spirits in the same category"
    )
    flavor_tags: list[str] = Field(default_factory=list)


class BrandDashboardResponse(BaseModel):
    """Complete intelligence dashboard for brand houses."""

    brand_id: uuid.UUID
    brand_name: str
    brand_slug: str
    total_products: int
    total_skus: int
    total_licensed_stockists: int
    total_orders: int
    total_gross_revenue_minor: int
    total_gross_revenue_formatted: str
    top_performing_skus: list[BrandSKUMarketShare] = Field(default_factory=list)
    regional_distribution: list[BrandRegionalDistribution] = Field(default_factory=list)
    taste_radars: list[BrandTasteRadarVisualization] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
