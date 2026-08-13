import pytest
from services.compliance.app.services.rider_service import RiderService


@pytest.mark.asyncio
async def test_rider_authorization_and_eligibility():
    svc = RiderService()
    auth = await svc.authorize_rider(
        rider_id="rider-d12-1",
        jurisdiction_id="IN-STATE-X",
    )

    assert auth["status"] == "VERIFIED"

    decision = await svc.get_eligibility("rider-d12-1", "IN-STATE-X")
    assert decision == "ALLOW"

    wrong_jur = await svc.get_eligibility("rider-d12-1", "IN-STATE-Z")
    assert wrong_jur == "DENY"
