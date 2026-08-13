"""
Master unit test for Phase D9 Order Management & Checkout Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.order.app.schemas.checkout import CheckoutRequest
from services.order.app.services.cart_service import CartService
from services.order.app.services.checkout_service import CheckoutService
from services.order.app.services.order_service import OrderService


@pytest.mark.asyncio
async def test_full_d9_order_checkout_pipeline():
    cart_svc = CartService()
    cart = await cart_svc.get_or_create_cart(customer_id="cust-master-d9", store_id="store-mumbai")
    await cart_svc.add_item(cart["id"], sku_id="sku-royal-750ml", quantity=2)

    checkout_svc = CheckoutService(cart_service=cart_svc)
    order = await checkout_svc.checkout(
        CheckoutRequest(
            cart_id=cart["id"],
            customer_id="cust-master-d9",
            store_id="store-mumbai",
            idempotency_key="checkout-master-d9-key",
        )
    )

    assert order["status"] == "PENDING_PAYMENT"

    order_svc = OrderService(checkout_service=checkout_svc)
    completed = await order_svc.complete_payment(order["id"], f"pay_{order['id']}")
    assert completed["status"] == "CONFIRMED"
