from uuid import uuid4


class PayoutService:

    def __init__(self):
        self.payouts: dict[str, dict] = {}

    async def calculate_payout(
        self,
        retailer_id: str,
        eligible_sales: int,
        refunds: int,
        platform_fee_pct: float = 0.05,
    ) -> int:

        net = eligible_sales - refunds
        fee = int(net * platform_fee_pct)
        payable = net - fee
        return max(0, payable)

    async def create_payout(
        self,
        retailer_id: str,
        amount: int,
        settlement_period: str,
        idempotency_key: str,
    ) -> dict:

        payout_id = str(uuid4())
        payout = {
            "id": payout_id,
            "retailer_id": retailer_id,
            "amount": amount,
            "currency": "INR",
            "status": "PROCESSING",
            "settlement_period": settlement_period,
            "idempotency_key": idempotency_key,
        }
        self.payouts[payout_id] = payout
        return payout
