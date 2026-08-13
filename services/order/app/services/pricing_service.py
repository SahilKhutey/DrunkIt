class PricingService:

    async def calculate(
        self,
        items: list,
        store_id: str,
        customer_id: str,
    ) -> dict:

        subtotal = 0
        taxes = 0

        for item in items:
            unit_price = getattr(item, "unit_price", None) or item.get("unit_price", 0)
            quantity = getattr(item, "quantity", None) or item.get("quantity", 0)
            tax_amount = getattr(item, "tax_amount", None) or item.get("tax_amount", 0)

            subtotal += unit_price * quantity
            taxes += tax_amount * quantity

        delivery_fee = 5000  # 50.00 INR in paise
        discount = 0

        total = subtotal + taxes + delivery_fee - discount
        if total < 0:
            total = 0

        return {
            "subtotal": subtotal,
            "taxes": taxes,
            "delivery_fee": delivery_fee,
            "discount": discount,
            "total": total,
        }
