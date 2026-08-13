import pytest
from services.order.app.schemas.checkout import CheckoutRequest
from services.order.app.services.cancellation_service import CancellationService
from services.order.app.services.cart_service import CartService
from services.order.app.services.checkout_service import CheckoutService
from services.order.app.services.order_service import OrderService


@pytest.mark.asyncio
async def test_order_cancellation_flow():
    cart_svc = CartService()
    cart = await cart_svc.get_or_create_cart(customer_id="cust-cancel", store_id="store-01")
    await cart_svc.add_item(cart["id"], sku_id="sku-100", quantity=1)

    checkout_svc = CheckoutService(cart_service=cart_svc)
    order = await checkout_svc.checkout(
        CheckoutRequest(
            cart_id=cart["id"],
            customer_id="cust-cancel",
            store_id="store-01",
            idempotency_key="checkout-key-cancel123",
        )
    )

    order_svc = OrderService(checkout_service=checkout_svc)
    cancel_svc = CancellationService(order_service=order_svc)

    cancelled_order = await cancel_svc.cancel(
        order_id=order["id"],
        reason="CUSTOMER_CHANGED_MIND",
        customer_id="cust-cancel",
    )

    assert cancelled_order["status"] == "CANCELLED"
    assert cancelled_order["cancellation_reason"] == "CUSTOMER_CHANGED_MIND"
