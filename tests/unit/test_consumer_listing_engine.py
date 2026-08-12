"""
Unit tests for Consumer Listing Engine Architecture (Quick Commerce + Trust Commerce, 18 Modules, 3 Template Types, Price Integrity).
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), "../../")))
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from faccp_common.consumer_listing import (
    ConsumerListingView, VisualIdentity, ProductIdentity, CommercialDetails, TrustDetails,
    ListingTemplateType, ListingTemplateRenderer, PriceIntegrityValidator, PriceDisplay
)
from scripts.constitution.check_consumer_listing_engine import ConsumerListingEngineChecker


def test_consumer_listing_view_modules():
    assert len(ConsumerListingView.ENGINE_MODULES) == 18


def test_listing_template_renderer():
    listing = ConsumerListingView(
        visual=VisualIdentity(product_image_url="https://s3/img.jpg", brand_name="Kingfisher", product_name="Premium Lager"),
        identity=ProductIdentity(product_id="prd_1", variant_name="Standard", pack_size="650ml"),
        commercial=CommercialDetails(mrp=220.0, selling_price=200.0, discount_percentage=9.09),
        availability_status="IN_STOCK",
        store_name="Mumbai Central Store",
        eta_minutes="20-30 min",
        trust=TrustDetails(seller_verified=True, listing_verified=True),
        actions={"view": True, "add_to_cart": True},
    )
    renderer = ListingTemplateRenderer()

    compact = renderer.render(listing, ListingTemplateType.COMPACT_CARD)
    assert compact["template_type"] == "COMPACT_CARD"

    regulated = renderer.render(listing, ListingTemplateType.REGULATED_CARD)
    assert regulated["seller_verified"] is True


def test_price_integrity_validator():
    assert PriceIntegrityValidator.validate_price_chain(200.0, 200.0, 200.0) is True
    assert PriceIntegrityValidator.validate_price_chain(200.0, 250.0, 200.0) is False


def test_consumer_listing_engine_checker():
    checker = ConsumerListingEngineChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
