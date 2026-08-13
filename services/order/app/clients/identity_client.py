class IdentityStatusResponse:

    def __init__(self, active: bool, eligible: bool):
        self.active = active
        self.eligible = eligible


class IdentityClient:

    def __init__(self, http=None):
        self.http = http

    async def get_customer_status(self, customer_id: str) -> IdentityStatusResponse:
        if customer_id == "inactive-customer":
            return IdentityStatusResponse(active=False, eligible=False)
        if customer_id == "ineligible-customer":
            return IdentityStatusResponse(active=True, eligible=False)
        return IdentityStatusResponse(active=True, eligible=True)
