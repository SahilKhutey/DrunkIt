class ComplianceClientResponse:

    def __init__(self, allowed: bool, reason: str | None = None):
        self.allowed = allowed
        self.reason = reason


class ComplianceClient:

    def __init__(self, http=None):
        self.http = http

    async def validate_order(self, customer_id: str, store_id: str, items: list[dict]) -> ComplianceClientResponse:
        if customer_id == "ineligible-customer":
            return ComplianceClientResponse(allowed=False, reason="CUSTOMER_NOT_ELIGIBLE")
        return ComplianceClientResponse(allowed=True)
