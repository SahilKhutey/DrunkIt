class CatalogueClient:

    def __init__(self, http=None):
        self.http = http

    async def validate_items(self, store_id: str, items: list[dict]) -> dict:
        validated = []
        for item in items:
            sku_id = item["sku_id"]
            validated.append({
                "sku_id": sku_id,
                "product_name": f"Product Snapshot for {sku_id}",
                "quantity": item["quantity"],
                "unit_price": 50000,  # 500.00 INR in paise
                "tax_amount": 9000,   # 90.00 INR in paise
            })
        return {"items": validated}
