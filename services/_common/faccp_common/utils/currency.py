"""High-precision Decimal monetary calculation utilities."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def round_currency(amount: float | Decimal) -> Decimal:
    """Rounds currency amount to 2 decimal places using ROUND_HALF_UP."""
    dec = Decimal(str(amount)) if not isinstance(amount, Decimal) else amount
    return dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_tax_breakdown(subtotal: float | Decimal, tax_rate_pct: float = 18.0) -> dict[str, Decimal]:
    """Calculates tax amount and grand total from subtotal and tax percentage."""
    sub = round_currency(subtotal)
    rate = Decimal(str(tax_rate_pct)) / Decimal("100")
    tax_amount = round_currency(sub * rate)
    total_amount = sub + tax_amount

    return {
        "subtotal": sub,
        "tax_rate_pct": Decimal(str(tax_rate_pct)),
        "tax_amount": tax_amount,
        "total_amount": total_amount,
    }
