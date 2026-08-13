"""
Master unit test for Phase D7 Regulatory Product Catalogue & SKU Intelligence Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.catalogue.app.schemas.product import ProductCreate
from services.catalogue.app.schemas.sku import SKUCreate
from services.catalogue.app.services.catalogue_service import CatalogueService
from services.catalogue.app.services.product_service import ProductService
from services.catalogue.app.services.sku_service import SKUService


@pytest.mark.asyncio
async def test_full_d7_regulatory_catalogue_pipeline():
    prod_svc = ProductService()
    sku_svc = SKUService()
    cat_svc = CatalogueService()

    product = await prod_svc.create(
        ProductCreate(
            product_code="PROD-ROYAL",
            name="Royal Challenge Whisky",
            brand_id="brand-rc",
            category="WHISKY",
            regulated=True,
        )
    )
    assert product["active"] is True

    sku = await sku_svc.create(
        SKUCreate(
            product_id=product["id"],
            sku_code="SKU-RC-750ML",
            volume_ml=750,
            packaging_type="BOTTLE",
        )
    )
    assert sku["sku_code"] == "SKU-RC-750ML"

    can_list = await cat_svc.can_list(
        sku_id=sku["id"],
        retailer_id="RET-STORE-01",
        store_id="STORE-MUMBAI-01",
        jurisdiction="MAHARASHTRA",
    )
    assert can_list["allowed"] is True
