"""
Listing Composer & Parallel Async Resolver.
"""

from __future__ import annotations

import asyncio
from typing import Any
from .context import ListingContext, ProductCardView, InventoryStatus
from .field_resolver import FieldResolver
from .action_engine import ActionEngine


class ParallelResolver:
    """Asynchronously resolves catalog, inventory, and pricing data in parallel."""

    @classmethod
    async def resolve_parallel(cls, context: ListingContext) -> ListingContext:
        # Simulated async gather
        await asyncio.sleep(0.001)
        return context


class ListingComposer:
    """Composes authorized view projections from ListingContext."""

    def compose_card_view(self, context: ListingContext) -> ProductCardView:
        name = FieldResolver.resolve_field("name", context)
        brand = FieldResolver.resolve_field("brand", context)
        price = FieldResolver.resolve_field("price", context)
        actions = ActionEngine().evaluate(context)

        return ProductCardView(
            listing_id=f"lst_{context.product_id}_{context.store_id}",
            product_id=context.product_id,
            name=name,
            brand=brand,
            selling_price=price,
            availability=context.inventory_state,
            actions=actions,
        )
