"""
Action & Eligibility Engine.
"""

from __future__ import annotations

from enum import Enum
from .context import ListingContext, InventoryStatus


class EligibilityState(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    ELIGIBILITY_REQUIRED = "ELIGIBILITY_REQUIRED"
    ELIGIBILITY_BLOCKED = "ELIGIBILITY_BLOCKED"


class ActionEngine:
    """Evaluates server-side action permissions (view, add_to_cart, purchase)."""

    def evaluate(self, context: ListingContext) -> dict[str, bool]:
        can_view = context.policy_state.get("can_view", True)
        is_eligible = context.user_context.get("is_age_verified", False)
        has_stock = context.inventory_state != InventoryStatus.OUT_OF_STOCK
        price_available = "selling_price" in context.pricing_state

        can_transact = can_view and is_eligible and has_stock and price_available
        return {
            "view": can_view,
            "add_to_cart": can_transact,
            "purchase": can_transact,
        }
