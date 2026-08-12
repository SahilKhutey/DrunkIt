"""
Price Integrity Engine.
Enforces DISPLAYED PRICE == CART PRICE == CHECKOUT PRICE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone



@dataclass
class PriceDisplay:
    mrp: float
    selling_price: float
    discount_amount: float
    discount_percentage: float
    tax_included: bool = True
    tax_amount: float = 0.0
    currency: str = "INR"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PriceIntegrityValidator:
    """Enforces strict server-side price integrity across product, cart, and checkout."""

    @classmethod
    def validate_price_chain(cls, product_price: float, cart_price: float, checkout_price: float) -> bool:
        return abs(product_price - cart_price) < 0.01 and abs(cart_price - checkout_price) < 0.01
