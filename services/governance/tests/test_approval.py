import pytest
from services.governance.app.services.approval_service import ApprovalService


@pytest.mark.asyncio
async def test_approval_workflow_and_self_approval_block():
    svc = ApprovalService()
    req = await svc.create_request("requester_admin", "POLICY_ACTIVATION", "POLICY", "pol-100", risk_level="HIGH")
    assert req["status"] == "PENDING"
    assert req["required_approvals"] == 2

    # Self approval forbidden
    with pytest.raises(PermissionError, match="SELF_APPROVAL_FORBIDDEN"):
        await svc.approve_request(req["id"], "requester_admin")

    appr1 = await svc.approve_request(req["id"], "approver_one")
    assert appr1["status"] == "PENDING"

    appr2 = await svc.approve_request(req["id"], "approver_two")
    assert appr2["status"] == "APPROVED"
