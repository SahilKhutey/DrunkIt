import pytest
from services.order.app.schemas.checkout import CheckoutRequest
from services.order.app.services.cart_service import CartService
from services.order.app.services.checkout_service import CheckoutService


@pytest.mark.asyncio
async def test_checkout_idempotency():
    cart_svc = CartService()
    cart = await cart_svc.get_or_create_cart(customer_id="cust-idemp", store_id="store-01")
    await cart_svc.add_item(cart["id"], sku_id="sku-100", quantity=1)

    checkout_svc = CheckoutService(cart_service=cart_svc)
    req = CheckoutRequest(
        cart_id=cart["id"],
        customer_id="cust-idemp",
        store_id="store-01",
        idempotency_key="checkout-idemp-999999",
    )

    first = await checkout_svc.checkout(req)
    second = await checkout_svc.checkout(req)

    assert first["id"] == second["id"]
    assert first["status"] == second["status"]
