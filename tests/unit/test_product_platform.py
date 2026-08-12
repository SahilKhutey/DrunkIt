"""
Unit tests for Product Platform Architecture (Product Master vs View Projections, 16 Modules, 7 Visibility Levels, 9 Lifecycle States).
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

from faccp_common.product import (
    ProductMaster, ProductLifecycleState, VisibilityLevel, ViewComposer,
    ConsumerProductView, AdminProductView, AttributeCatalog
)
from scripts.constitution.check_product_platform import ProductPlatformChecker


def test_product_master_module_count():
    assert len(ProductMaster.CATALOG_MODULES) == 16
    assert len(ProductLifecycleState) == 9
    assert len(VisibilityLevel) == 7


def test_attribute_catalog():
    assert "abv" in AttributeCatalog.CORE_ATTRIBUTES
    assert AttributeCatalog.CORE_ATTRIBUTES["abv"].required is True


def test_view_composer():
    product = ProductMaster(
        product_id="prd_100",
        brand_id="brd_1",
        name="Premium Craft Beer",
        category_id="cat_beer",
        description="Craft brewed lager",
        manufacturer="Craft Brewery Co.",
        attributes={"brand_name": "Craft Master"},
    )
    composer = ViewComposer()

    # Anonymous view
    view_anon = composer.compose_consumer_view(product, price=250.0, availability="IN_STOCK", user_visibility=VisibilityLevel.PUBLIC)
    assert view_anon.actions["add_to_cart"] is False

    # Eligible consumer view
    view_eligible = composer.compose_consumer_view(product, price=250.0, availability="IN_STOCK", user_visibility=VisibilityLevel.TRANSACTION_ELIGIBLE)
    assert view_eligible.actions["add_to_cart"] is True

    # Admin view
    admin_view = composer.compose_admin_view(product)
    assert admin_view.product_id == "prd_100"


def test_product_platform_checker():
    checker = ProductPlatformChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
