import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/policy-service")))

import pytest
from policy_app.models import (
    EvaluatePolicyRequest, SubjectAttributes, ResourceAttributes, EnvironmentAttributes,
    SystemRole, PermissionAction, PrivacyClassification, BreakGlassLevel
)
from policy_app.rbac_matrix import check_rbac_permission
from policy_app.abac_rules import evaluate_abac_rules
from policy_app.sod_detector import record_user_action, check_sod_violation

def test_rbac_permission_matrix():
    assert check_rbac_permission(SystemRole.SUPER_ADMIN, "ANY", PermissionAction.CREATE) is True
    assert check_rbac_permission(SystemRole.STATE_ADMIN, "EXCISE_LICENSE", PermissionAction.APPROVE) is True
    assert check_rbac_permission(SystemRole.GUEST, "ORDER", PermissionAction.CREATE) is False

def test_abac_geographic_containment_pass():
    req = EvaluatePolicyRequest(
        subject=SubjectAttributes(
            user_id="U-100",
            role=SystemRole.STATE_ADMIN,
            assigned_jurisdictions=["IN-KA"]
        ),
        action=PermissionAction.APPROVE,
        resource=ResourceAttributes(
            resource_id="LIC-KA-001",
            resource_type="EXCISE_LICENSE",
            jurisdiction="IN-KA"
        ),
        environment=EnvironmentAttributes(
            timestamp_iso="2026-08-11T12:00:00Z",
            client_ip="127.0.0.1",
            geo_jurisdiction="IN-KA"
        )
    )
    decision, rule_id, reason, step_up = evaluate_abac_rules(req)
    assert decision == "ALLOW"

def test_abac_geographic_containment_denial():
    req = EvaluatePolicyRequest(
        subject=SubjectAttributes(
            user_id="U-100",
            role=SystemRole.STATE_ADMIN,
            assigned_jurisdictions=["IN-KA"]
        ),
        action=PermissionAction.APPROVE,
        resource=ResourceAttributes(
            resource_id="LIC-MH-001",
            resource_type="EXCISE_LICENSE",
            jurisdiction="IN-MH"
        ),
        environment=EnvironmentAttributes(
            timestamp_iso="2026-08-11T12:00:00Z",
            client_ip="127.0.0.1",
            geo_jurisdiction="IN-MH"
        )
    )
    decision, rule_id, reason, step_up = evaluate_abac_rules(req)
    assert decision == "DENY"
    assert "RULE_4_1_GEO_CONTAINMENT" in rule_id

def test_sod_15min_conflict_enforcement():
    user_id = "STAFF-99"
    res_id = "RET-APP-440"

    # User initiates application
    record_user_action(user_id, res_id, "INITIATE")

    # User attempts to approve the same application immediately
    is_conflict, reason = check_sod_violation(user_id, res_id, "APPROVE")
    assert is_conflict is True
    assert "SoD Violation" in reason

def test_p3_data_isolation_denial():
    req = EvaluatePolicyRequest(
        subject=SubjectAttributes(
            user_id="STORE-MGR-01",
            role=SystemRole.STORE_MANAGER
        ),
        action=PermissionAction.READ,
        resource=ResourceAttributes(
            resource_id="ID-DOC-882",
            resource_type="IDENTITY_DOCUMENT",
            jurisdiction="IN-KA",
            classification=PrivacyClassification.P3_IDENTITY_KYC
        ),
        environment=EnvironmentAttributes(
            timestamp_iso="2026-08-11T12:00:00Z",
            client_ip="127.0.0.1",
            geo_jurisdiction="IN-KA"
        )
    )
    decision, rule_id, reason, step_up = evaluate_abac_rules(req)
    assert decision == "DENY"
    assert "RULE_4_4_P3_ISOLATION" in rule_id

def test_break_glass_override():
    req = EvaluatePolicyRequest(
        subject=SubjectAttributes(
            user_id="SEC-ADM-01",
            role=SystemRole.SECURITY_ADMIN,
            break_glass_level=BreakGlassLevel.LEVEL_1_FRAUD
        ),
        action=PermissionAction.READ,
        resource=ResourceAttributes(
            resource_id="ID-DOC-882",
            resource_type="IDENTITY_DOCUMENT",
            jurisdiction="IN-KA",
            classification=PrivacyClassification.P3_IDENTITY_KYC
        ),
        environment=EnvironmentAttributes(
            timestamp_iso="2026-08-11T12:00:00Z",
            client_ip="127.0.0.1",
            geo_jurisdiction="IN-KA"
        )
    )
    decision, rule_id, reason, step_up = evaluate_abac_rules(req)
    assert decision == "ALLOW"
    assert rule_id == "BREAK_GLASS_OVERRIDE"
