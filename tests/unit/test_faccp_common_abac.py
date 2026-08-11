import pytest
from faccp_common.abac import (
    ABACEngine, AccessRequest, SubjectAttributes, ResourceAttributes,
    ActionAttributes, EnvironmentAttributes, build_default_policies,
)


def test_faccp_common_abac_engine_permit_consumer_own():
    engine = ABACEngine(build_default_policies())
    req = AccessRequest(
        subject=SubjectAttributes(user_id="usr-101", primary_role="CONSUMER", roles=["CONSUMER"]),
        resource=ResourceAttributes(resource_type="consumer", owner_id="usr-101", classification="P1"),
        action=ActionAttributes(action="read"),
        environment=EnvironmentAttributes(),
    )
    decision = engine.evaluate(req)
    assert decision.is_permit is True
    assert decision.effect == "PERMIT"


def test_faccp_common_abac_engine_deny_p3_isolation():
    engine = ABACEngine(build_default_policies())
    req = AccessRequest(
        subject=SubjectAttributes(user_id="mgr-1", primary_role="STORE_MANAGER", roles=["STORE_MANAGER"]),
        resource=ResourceAttributes(resource_type="consumer", owner_id="usr-101", classification="P3"),
        action=ActionAttributes(action="read"),
        environment=EnvironmentAttributes(),
    )
    decision = engine.evaluate(req)
    assert decision.is_deny is True
    assert decision.effect == "DENY"


def test_faccp_common_abac_engine_deny_global_locked_user():
    engine = ABACEngine(build_default_policies())
    req = AccessRequest(
        subject=SubjectAttributes(user_id="usr-99", primary_role="CONSUMER", roles=["CONSUMER"], is_locked=True),
        resource=ResourceAttributes(resource_type="consumer", owner_id="usr-99", classification="P1"),
        action=ActionAttributes(action="read"),
        environment=EnvironmentAttributes(),
    )
    decision = engine.evaluate(req)
    assert decision.is_deny is True
    assert "Locked users are denied all access" in decision.reason
