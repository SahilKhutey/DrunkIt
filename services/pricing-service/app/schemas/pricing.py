from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, Field


class PriceBookEntryRequest(BaseModel):
    product_id: str
    sku: str
    base_price: Decimal = Field(ge=0)
    min_quantity: int = 1
    max_quantity: int | None = None


class CreatePriceBookRequest(BaseModel):
    name: str
    store_id: str
    retailer_id: str
    effective_from: date
    effective_until: date | None = None
    entries: list[PriceBookEntryRequest]


class CreatePromotionRequest(BaseModel):
    code: str
    name: str
    description: str | None = None
    discount_type: Literal["percentage", "fixed"]
    discount_value: Decimal
    min_order_amount: Decimal = Decimal("0")
    max_discount_amount: Decimal | None = None
    applicable_categories: list[str] = Field(default_factory=list)
    applicable_products: list[str] = Field(default_factory=list)
    valid_from: datetime
    valid_until: datetime
    max_total_uses: int | None = None
    max_uses_per_user: int | None = None


class PriceLineItem(BaseModel):
    product_id: str
    sku: str
    quantity: int = Field(ge=1)
    unit_price: Decimal | None = None
    category: str | None = None


class CalculateRequest(BaseModel):
    store_id: str
    jurisdiction_code: str
    currency: str = "INR"
    items: list[PriceLineItem]
    promotion_code: str | None = None
    delivery_fee: Decimal = Decimal("0")
    metadata: dict[str, Any] = Field(default_factory=dict)


class CalculateResponse(BaseModel):
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    platform_fee: Decimal
    total_amount: Decimal
    currency: str
    applied_promotion: str | None
    line_items: list[dict[str, Any]]
    snapshot_id: str
    calculated_at: datetime
