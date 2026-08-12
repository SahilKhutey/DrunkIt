"""
Unit tests for Listing Engine Development Specification (Read-Optimized Composition Engine, 17 Modules, 8 Templates, FieldResolver, ActionEngine).
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from faccp_common.listing_service import (
    ListingContext, ProductCardView, ProductDetailView, ListingStatus, InventoryStatus,
    FieldResolver, ActionEngine, EligibilityState, ListingComposer
)
from scripts.constitution.check_listing_engine_spec import ListingEngineSpecChecker


def test_listing_spec_modules():
    assert len(ProductDetailView.CORE_MODULES) == 17
    assert len(ProductDetailView.TEMPLATE_TYPES) == 8
    assert len(ListingStatus) == 7
    assert len(InventoryStatus) == 4


def test_field_resolver():
    ctx = ListingContext(
        product_id="prd_100",
        sku_id="sku_100",
        retailer_id="ret_1",
        store_id="str_1",
        product_data={"name": "Kingfisher Lager", "brand": "Kingfisher"},
        pricing_state={"selling_price": 180.0},
    )
    name = FieldResolver.resolve_field("name", ctx)
    brand = FieldResolver.resolve_field("brand", ctx)
    price = FieldResolver.resolve_field("price", ctx)

    assert name == "Kingfisher Lager"
    assert brand == "Kingfisher"
    assert price == 180.0


def test_action_engine_fail_closed():
    ctx_no_auth = ListingContext(
        product_id="prd_100",
        sku_id="sku_100",
        retailer_id="ret_1",
        store_id="str_1",
        inventory_state=InventoryStatus.IN_STOCK,
        pricing_state={"selling_price": 180.0},
        user_context={"is_age_verified": False},
    )
    actions = ActionEngine().evaluate(ctx_no_auth)
    assert actions["view"] is True
    assert actions["add_to_cart"] is False


@pytest.mark.asyncio
async def test_listing_composer():
    ctx = ListingContext(
        product_id="prd_100",
        sku_id="sku_100",
        retailer_id="ret_1",
        store_id="str_1",
        product_data={"name": "Kingfisher Lager", "brand": "Kingfisher"},
        pricing_state={"selling_price": 180.0},
        user_context={"is_age_verified": True},
    )
    composer = ListingComposer()
    card = composer.compose_card_view(ctx)
    assert card.name == "Kingfisher Lager"
    assert card.actions["add_to_cart"] is True


def test_listing_engine_spec_checker():
    checker = ListingEngineSpecChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
