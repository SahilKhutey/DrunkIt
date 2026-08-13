import pytest
from services.catalogue.app.schemas.product import ProductCreate
from services.catalogue.app.services.product_service import ProductService


@pytest.mark.asyncio
async def test_product_code_unique():
    service = ProductService()

    await service.create(
        ProductCreate(
            product_code="PROD-001",
            name="Test Whisky",
            brand_id="brand-1",
            category="WHISKY",
        )
    )

    with pytest.raises(ValueError, match="Product code already exists"):
        await service.create(
            ProductCreate(
                product_code="PROD-001",
                name="Duplicate Test",
                brand_id="brand-1",
                category="WHISKY",
            )
        )
