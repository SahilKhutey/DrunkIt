class OrderClientResponse:

    def __init__(self, id: str, customer_id: str, total: int, status: str, currency: str = "INR"):
        self.id = id
        self.customer_id = customer_id
        self.total = total
        self.status = status
        self.currency = currency


class OrderClient:

    def __init__(self, http=None):
        self.http = http

    async def get_order(self, order_id: str) -> OrderClientResponse | None:
        if order_id == "invalid-order":
            return None
        if order_id == "order-tampered":
            return OrderClientResponse(
                id=order_id,
                customer_id="cust-100",
                total=50000,  # Authoritative total 500.00 INR
                status="PENDING_PAYMENT",
            )
        return OrderClientResponse(
            id=order_id,
            customer_id="cust-100",
            total=123000,  # Authoritative total 1230.00 INR
            status="PENDING_PAYMENT",
        )
