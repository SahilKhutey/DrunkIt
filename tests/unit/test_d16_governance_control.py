"""
Master unit test for Phase D16 Audit, Governance, Policy & Regulatory Control Plane.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.governance.app.engine.audit_engine import AuditEngine
from services.governance.app.engine.consent_engine import ConsentEngine
from services.governance.app.engine.evidence_engine import EvidenceEngine
from services.governance.app.engine.policy_engine import PolicyEngine
from services.governance.app.engine.retention_engine import RetentionEngine
from services.governance.app.security.hashing import calculate_event_hash, verify_event_chain
from services.governance.app.services.approval_service import ApprovalService
from services.governance.app.services.audit_service import AuditService
from services.governance.app.services.governance_service import GovernanceService
from services.governance.app.services.policy_service import PolicyService


@pytest.mark.asyncio
async def test_full_d16_governance_control_pipeline():
    # 1. Audit Engine Chained SHA-256 Event Recording
    audit_svc = AuditService()
    e1 = await audit_svc.record_event({"event_type": "order.created", "action": "CREATE_ORDER", "subject_id": "ord-surat-100", "correlation_id": "corr-surat-1"})
    e2 = await audit_svc.record_event({"event_type": "payment.authorized", "action": "PAYMENT_AUTHORIZE", "subject_id": "ord-surat-100", "correlation_id": "corr-surat-1"})

    assert e1["sequence_number"] == 1001
    assert e2["sequence_number"] == 1002
    assert e2["previous_hash"] == e1["event_hash"]
    assert await audit_svc.verify_audit_chain() is True

    # 2. Versioned Policy Engine (Restricted DSL without eval)
    pol_svc = PolicyService()
    rules = [{"id": "age_check", "condition": {"field": "consumer.age", "operator": "greater_than", "value": 21}, "action": "ALLOW"}]
    pol = await pol_svc.create_policy("Age Check Policy", "IN-GJ", "CONSUMER_VERIFICATION", rules)
    assert pol["status"] == "DRAFT"

    await pol_svc.transition_status(pol["policy_id"], "REVIEW")
    await pol_svc.transition_status(pol["policy_id"], "APPROVED")
    await pol_svc.transition_status(pol["policy_id"], "ACTIVE")

    eval_res = await pol_svc.evaluate_policy(pol["policy_id"], {"consumer": {"age": 24}})
    assert eval_res["decision"] == "ALLOW"

    # 3. Privacy-Preserving Evidence Engine
    evidence_eng = EvidenceEngine()
    ev = await evidence_eng.record_evidence("PERMIT_DOC", "CONSUMER", "cons-surat-1", "STATE_EXCISE", "ref-permit-505")
    assert ev["evidence_id"].startswith("ev_")

    # 4. Consent Registry
    consent_eng = ConsentEngine()
    await consent_eng.grant_consent("cons-surat-1", "TERMS_AND_CONDITIONS")
    assert await consent_eng.has_valid_consent("cons-surat-1", "TERMS_AND_CONDITIONS") is True

    # 5. Administrative Multi-Approval Workflow & Separation of Duties
    approval_svc = ApprovalService()
    req = await approval_svc.create_request("admin_requester", "POLICY_ACTIVATION", "POLICY", pol["policy_id"], risk_level="HIGH")
    assert req["required_approvals"] == 2

    with pytest.raises(PermissionError):
        await approval_svc.approve_request(req["id"], "admin_requester")

    await approval_svc.approve_request(req["id"], "approver_1")
    appr_final = await approval_svc.approve_request(req["id"], "approver_2")
    assert appr_final["status"] == "APPROVED"

    # 6. Retention & Legal Hold Engine
    ret_eng = RetentionEngine()
    ret_eng.add_legal_hold("cons-surat-1")
    assert ret_eng.can_delete("cons-surat-1") is False
    ret_eng.release_legal_hold("cons-surat-1")

    # 7. Compliance Reporting
    gov_svc = GovernanceService()
    rep = await gov_svc.generate_report("AUDIT_SUMMARY", 30)
    assert rep["status"] == "COMPLETED"
