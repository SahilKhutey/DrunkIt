import pytest
from services.catalogue.app.services.catalogue_service import CatalogueService


@pytest.mark.asyncio
async def test_unapproved_sku_cannot_list():
    service = CatalogueService()

    result = await service.can_list(
        sku_id="blocked-sku",
        retailer_id="RET-1",
        store_id="STORE-1",
        jurisdiction="STATE-A",
    )

    assert result["allowed"] is False
    assert result["reason"] == "COMPLIANCE_BLOCKED"


@pytest.mark.asyncio
async def test_inactive_retailer_cannot_list():
    service = CatalogueService()

    result = await service.can_list(
        sku_id="SKU-1",
        retailer_id="inactive-retailer",
        store_id="STORE-1",
        jurisdiction="STATE-A",
    )

    assert result["allowed"] is False
    assert result["reason"] == "RETAILER_INACTIVE"
