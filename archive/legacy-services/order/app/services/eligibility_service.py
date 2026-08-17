from services.order.app.clients.compliance_client import ComplianceClient
from services.order.app.clients.identity_client import IdentityClient


class EligibilityService:

    def __init__(
        self,
        identity_client: IdentityClient | None = None,
        compliance_client: ComplianceClient | None = None,
    ):
        self.identity = identity_client or IdentityClient()
        self.compliance = compliance_client or ComplianceClient()

    async def validate(
        self,
        customer_id: str,
        store_id: str,
        items: list,
    ) -> bool:

        identity = await self.identity.get_customer_status(customer_id)

        if not identity.active:
            raise ValueError("CUSTOMER_INACTIVE")

        if not identity.eligible:
            raise ValueError("CUSTOMER_NOT_ELIGIBLE")

        result = await self.compliance.validate_order(
            customer_id=customer_id,
            store_id=store_id,
            items=items,
        )

        if not result.allowed:
            raise ValueError(result.reason or "ORDER_COMPLIANCE_FAILED")

        return True
