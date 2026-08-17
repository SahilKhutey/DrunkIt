import pytest
from services.governance.app.services.policy_service import PolicyService


@pytest.mark.asyncio
async def test_policy_creation_and_transition():
    svc = PolicyService()
    rules = [
        {"id": "check_age", "condition": {"field": "consumer.age", "operator": "greater_than", "value": 21}, "action": "ALLOW"}
    ]
    pol = await svc.create_policy("Age Limits", "IN-GJ", "CONSUMER_VERIFICATION", rules)
    assert pol["status"] == "DRAFT"

    rev = await svc.transition_status(pol["policy_id"], "REVIEW")
    assert rev["status"] == "REVIEW"

    appr = await svc.transition_status(pol["policy_id"], "APPROVED")
    assert appr["status"] == "APPROVED"

    act = await svc.transition_status(pol["policy_id"], "ACTIVE")
    assert act["status"] == "ACTIVE"

    eval_res = await svc.evaluate_policy(pol["policy_id"], {"consumer": {"age": 25}})
    assert eval_res["decision"] == "ALLOW"
