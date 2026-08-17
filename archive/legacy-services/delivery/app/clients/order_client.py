class OrderClient:

    def __init__(self, http=None):
        self.http = http

    async def get_order_details(self, order_id: str) -> dict:
        return {
            "id": order_id,
            "status": "CONFIRMED",
            "regulated_product": True,
        }
