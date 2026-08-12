"""
View Composer Engine (Projections Layer).
Separates internal Product Master truth from audience-specific views.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from .master import ProductMaster, VisibilityLevel


@dataclass
class ConsumerProductView:
    product_id: str
    name: str
    brand_name: str
    price_amount: float
    currency: str
    availability_state: str
    actions: dict[str, bool] = field(default_factory=dict)


@dataclass
class RetailerProductView:
    product_id: str
    name: str
    sku_code: str
    store_id: str
    price_amount: float
    stock_quantity: int
    listing_status: str


@dataclass
class AdminProductView:
    product_id: str
    name: str
    state: str
    version: str
    compliance_metadata: dict[str, Any]
    audit_notes: list[str] = field(default_factory=list)


@dataclass
class SearchProductView:
    product_id: str
    name: str
    brand: str
    category: str
    price: float
    availability: str


class ViewComposer:
    """Composes audience-specific projections from Product Master and context."""

    def compose_consumer_view(
        self, product: ProductMaster, price: float, availability: str, user_visibility: VisibilityLevel
    ) -> ConsumerProductView:
        can_purchase = user_visibility >= VisibilityLevel.TRANSACTION_ELIGIBLE
        return ConsumerProductView(
            product_id=product.product_id,
            name=product.name,
            brand_name=product.attributes.get("brand_name", "Unknown"),
            price_amount=price,
            currency="INR",
            availability_state=availability,
            actions={
                "view": True,
                "add_to_cart": can_purchase,
                "purchase": can_purchase,
            },
        )

    def compose_admin_view(self, product: ProductMaster) -> AdminProductView:
        return AdminProductView(
            product_id=product.product_id,
            name=product.name,
            state=product.state.value,
            version=product.version,
            compliance_metadata=product.compliance_metadata,
        )
