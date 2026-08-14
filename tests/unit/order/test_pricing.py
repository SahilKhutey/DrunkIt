"""Unit tests for PricingService Decimal calculations."""

from decimal import Decimal
from services.order.app.services.pricing_service import PricingService


def test_pricing_calculation():
    service = PricingService()
    item = type("Item", (), {"unit_price": Decimal("100.00"), "quantity": Decimal("2")})()
    result = service.calculate([item], delivery_fee=Decimal("20.00"))
    assert result["subtotal"] == Decimal("200.00")
    assert result["delivery_fee"] == Decimal("20.00")
    assert result["total"] == Decimal("220.00")


def test_pricing_rounding():
    service = PricingService()
    item = type("Item", (), {"unit_price": Decimal("10.99"), "quantity": Decimal("3")})()
    result = service.calculate([item], tax=Decimal("2.475"))
    assert result["subtotal"] == Decimal("32.97")
    assert result["tax"] == Decimal("2.48")
    assert result["total"] == Decimal("35.45")
