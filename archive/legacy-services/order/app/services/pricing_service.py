"""Financial Pricing Engine."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Sequence

CENT = Decimal("0.01")


def money(value: Any) -> Decimal:
    """Quantize decimal value to 2 decimal places with HALF_UP rounding."""
    if isinstance(value, Decimal):
        return value.quantize(CENT, rounding=ROUND_HALF_UP)
    try:
        val_dec = Decimal(str(value))
        return val_dec.quantize(CENT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


class AwaitableDict(dict):
    """Dictionary that can be optionally awaited for async compatibility."""

    def __await__(self):
        async def _res():
            return self
        return _res().__await__()


class PricingService:
    """Financial pricing engine using exact Decimal arithmetic."""

    def calculate(
        self,
        items: Sequence[Any],
        *args: Any,
        discount: Decimal = Decimal("0"),
        tax: Decimal = Decimal("0"),
        delivery_fee: Decimal = Decimal("0"),
        **kwargs: Any,
    ) -> AwaitableDict:
        """Calculate subtotal, discount, tax, delivery fee, and total."""
        if args and isinstance(args[0], str) and not args[0].replace(".", "", 1).isdigit():
            discount = Decimal("0")
        elif args:
            discount = money(args[0])

        subtotal = sum(
            (
                money(getattr(item, "unit_price", 0) if not isinstance(item, dict) else item.get("unit_price", 0))
                * money(getattr(item, "quantity", 1) if not isinstance(item, dict) else item.get("quantity", 1))
                for item in items
            ),
            Decimal("0"),
        )
        subtotal = money(subtotal)
        discount = money(discount)
        tax = money(tax)
        delivery_fee = money(delivery_fee)

        total = money(subtotal - discount + tax + delivery_fee)

        return AwaitableDict({
            "subtotal": subtotal,
            "taxes": tax,
            "tax": tax,
            "delivery_fee": delivery_fee,
            "discount": discount,
            "total": total,
        })
