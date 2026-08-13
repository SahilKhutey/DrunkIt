import pytest
from services.order.app.services.cart_service import CartService


@pytest.mark.asyncio
async def test_cart_create_and_add_items():
    service = CartService()
    cart = await service.get_or_create_cart(customer_id="cust-01", store_id="store-01")

    assert cart["customer_id"] == "cust-01"
    assert cart["status"] == "ACTIVE"

    item = await service.add_item(cart["id"], sku_id="sku-100", quantity=2)
    assert item["quantity"] == 2
