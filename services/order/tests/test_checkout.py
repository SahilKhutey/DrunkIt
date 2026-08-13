import pytest
from services.order.app.schemas.checkout import CheckoutRequest
from services.order.app.services.cart_service import CartService
from services.order.app.services.checkout_service import CheckoutService


@pytest.mark.asyncio
async def test_checkout_success():
    cart_svc = CartService()
    cart = await cart_svc.get_or_create_cart(customer_id="cust-01", store_id="store-01")
    await cart_svc.add_item(cart["id"], sku_id="sku-100", quantity=2)

    checkout_svc = CheckoutService(cart_service=cart_svc)
    order = await checkout_svc.checkout(
        CheckoutRequest(
            cart_id=cart["id"],
            customer_id="cust-01",
            store_id="store-01",
            idempotency_key="checkout-key-123456",
        )
    )

    assert order["status"] == "PENDING_PAYMENT"
    assert order["total"] > 0


@pytest.mark.asyncio
async def test_empty_cart_checkout_fails():
    cart_svc = CartService()
    cart = await cart_svc.get_or_create_cart(customer_id="cust-empty", store_id="store-01")

    checkout_svc = CheckoutService(cart_service=cart_svc)
    with pytest.raises(ValueError, match="CART_EMPTY"):
        await checkout_svc.checkout(
            CheckoutRequest(
                cart_id=cart["id"],
                customer_id="cust-empty",
                store_id="store-01",
                idempotency_key="checkout-key-empty123",
            )
        )
