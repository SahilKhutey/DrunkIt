import pytest
from datetime import datetime, timedelta, timezone
from services.compliance.app.engine.eligibility_engine import EligibilityEngine


@pytest.mark.asyncio
async def test_retailer_license_eligibility():
    engine = EligibilityEngine()
    now = datetime.now(timezone.utc)

    valid_licenses = [
        {
            "status": "VERIFIED",
            "jurisdiction_id": "IN-STATE-X",
            "valid_until": now + timedelta(days=100),
        }
    ]

    res = await engine.check_retailer_license(valid_licenses, "IN-STATE-X")
    assert res == "ALLOW"

    expired_licenses = [
        {
            "status": "VERIFIED",
            "jurisdiction_id": "IN-STATE-X",
            "valid_until": now - timedelta(days=10),
        }
    ]

    res_exp = await engine.check_retailer_license(expired_licenses, "IN-STATE-X")
    assert res_exp == "DENY"
