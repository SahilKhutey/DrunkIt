"""
Unit tests for Phase 5 Catalog Service (Schemas, Validation, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/catalog-service")
common_path = os.path.join(root_dir, "services/_common")

for mod_name in list(sys.modules.keys()):
    if mod_name == "app" or mod_name.startswith("app."):
        del sys.modules[mod_name]

if service_path not in sys.path:
    sys.path.insert(0, service_path)
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.schemas.catalog import CategoryCreate, BrandCreate, ProductCreate, StoreListingCreate
from scripts.constitution.check_catalog_service import CatalogServiceChecker


def test_category_create_valid():
    cat = CategoryCreate(
        code="WHISKY",
        name="Whisky & Bourbon",
        description="Single malt and blended whiskies",
    )
    assert cat.code == "WHISKY"
    assert cat.name == "Whisky & Bourbon"


def test_brand_create_valid():
    brand = BrandCreate(
        code="AMRUT",
        name="Amrut Single Malt",
        manufacturer="Amrut Distilleries",
        origin_country="IN",
    )
    assert brand.code == "AMRUT"
    assert brand.origin_country == "IN"


def test_product_create_valid():
    prod = ProductCreate(
        gtin="8901234567890",
        title="Amrut Fusion Single Malt Indian Whisky 750ml",
        brand_id="brand_amrut_001",
        category_id="cat_whisky_001",
        volume_ml=750,
        abv_percentage=50.0,
        packaging_type="GLASS_BOTTLE",
    )
    assert prod.gtin == "8901234567890"
    assert prod.volume_ml == 750


def test_catalog_service_checker():
    checker = CatalogServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
