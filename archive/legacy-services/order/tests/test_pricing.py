import pytest
from services.order.app.services.pricing_service import PricingService


@pytest.mark.asyncio
async def test_server_side_pricing_calculation():
    pricing_svc = PricingService()
    items = [
        {"unit_price": 50000, "quantity": 2, "tax_amount": 9000},
    ]

    res = await pricing_svc.calculate(items, store_id="store-1", customer_id="cust-1")
    # Subtotal: 50000 * 2 = 100000
    # Taxes: 9000 * 2 = 18000
    # Delivery fee: 5000
    # Total: 100000 + 18000 + 5000 = 123000
    assert res["subtotal"] == 100000
    assert res["taxes"] == 18000
    assert res["delivery_fee"] == 5000
    assert res["total"] == 123000
