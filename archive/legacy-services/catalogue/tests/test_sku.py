import pytest
from services.catalogue.app.schemas.sku import SKUCreate
from services.catalogue.app.services.sku_service import SKUService


@pytest.mark.asyncio
async def test_create_sku():
    service = SKUService()

    sku = await service.create(
        SKUCreate(
            product_id="prod-100",
            sku_code="SKU-750ML",
            volume_ml=750,
            packaging_type="BOTTLE",
        )
    )

    assert sku["sku_code"] == "SKU-750ML"
    assert sku["volume_ml"] == 750
