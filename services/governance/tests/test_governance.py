import pytest
from services.governance.app.services.governance_service import GovernanceService


@pytest.mark.asyncio
async def test_governance_reporting():
    svc = GovernanceService()
    rep = await svc.generate_report("COMPLIANCE_AUDIT", 30)
    assert rep["status"] == "COMPLETED"
    assert rep["summary"]["chain_integrity"] == "VERIFIED"
