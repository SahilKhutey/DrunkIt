import pytest
from services.security.app.services.case_service import CaseService


@pytest.mark.asyncio
async def test_case_creation_and_listing():
    svc = CaseService()
    case = await svc.create_case("CONSUMER", "cons-case-100", "ACCOUNT_TAKEOVER", "HIGH")
    assert case["status"] == "OPEN"

    all_cases = await svc.list_cases(status="OPEN")
    assert len(all_cases) == 1
    assert all_cases[0]["id"] == case["id"]
