import pytest
from services.compliance.app.services.retailer_service import RetailerService


@pytest.mark.asyncio
async def test_retailer_license_registration_and_eligibility():
    svc = RetailerService()
    lic = await svc.add_license(
        retailer_id="ret-d12-1",
        license_number="EXCISE-999-X",
        jurisdiction_id="IN-STATE-X",
    )

    assert lic["status"] == "VERIFIED"

    decision = await svc.get_eligibility("ret-d12-1", "IN-STATE-X")
    assert decision == "ALLOW"

    wrong_jur = await svc.get_eligibility("ret-d12-1", "IN-STATE-Y")
    assert wrong_jur == "DENY"
