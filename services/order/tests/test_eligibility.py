import pytest
from services.order.app.services.eligibility_service import EligibilityService


@pytest.mark.asyncio
async def test_ineligible_customer_blocked():
    eligibility_svc = EligibilityService()

    with pytest.raises(ValueError, match="CUSTOMER_NOT_ELIGIBLE"):
        await eligibility_svc.validate(
            customer_id="ineligible-customer",
            store_id="store-1",
            items=[],
        )
