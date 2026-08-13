"""
Master unit test for Phase D12 Compliance & Trust Engine.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.compliance.app.engine.context import ComplianceContext
from services.compliance.app.engine.decision_engine import DecisionEngine
from services.compliance.app.providers.excise_adapter import StateExciseAdapter
from services.compliance.app.services.audit_service import AuditService
from services.compliance.app.services.consumer_service import ConsumerService
from services.compliance.app.services.policy_service import PolicyService
from services.compliance.app.services.retailer_service import RetailerService
from services.compliance.app.services.rider_service import RiderService
from services.compliance.app.services.risk_service import RiskService


@pytest.mark.asyncio
async def test_full_d12_compliance_trust_pipeline():
    # 1. State Excise Integration
    adapter = StateExciseAdapter(state_code="IN-STATE-X")
    lic_res = await adapter.verify_license("EXCISE-SURAT-88")
    assert lic_res["verified"] is True

    # 2. Consumer Verification & Privacy Isolation
    cons_svc = ConsumerService()
    v_rec = await cons_svc.verify_consumer("cons-surat-100")
    assert v_rec["status"] == "VERIFIED"
    assert v_rec["verification_reference"].startswith("vrf_ref_")

    # 3. Retailer License Verification
    ret_svc = RetailerService()
    await ret_svc.add_license("ret-surat-100", "EXCISE-SURAT-88", "IN-STATE-X")
    ret_elig = await ret_svc.get_eligibility("ret-surat-100", "IN-STATE-X")
    assert ret_elig == "ALLOW"

    # 4. Rider Authorization
    rider_svc = RiderService()
    await rider_svc.authorize_rider("rider-surat-100", "IN-STATE-X")
    rider_elig = await rider_svc.get_eligibility("rider-surat-100", "IN-STATE-X")
    assert rider_elig == "ALLOW"

    # 5. Policy & 3-Way Decision Engine (ALLOW)
    pol_svc = PolicyService()
    dec_engine = DecisionEngine(policy_service=pol_svc)

    ctx_allow = ComplianceContext(
        consumer_id="cons-surat-100",
        retailer_id="ret-surat-100",
        rider_id="rider-surat-100",
        product_id="prod-beer-01",
        order_id="ord-surat-555",
        delivery_id="del-surat-555",
        jurisdiction_id="IN-STATE-X",
        operation="CREATE_ALCOHOL_ORDER",
        timestamp=datetime.now(timezone.utc),
    )
    setattr(ctx_allow, "consumer_verification_status", "VERIFIED")

    decision = await dec_engine.decide(ctx_allow)
    assert decision["decision"] == "ALLOW"

    # 6. Risk Scoring & Tamper-Evident SHA-256 Hashed Audit Event
    risk_svc = RiskService()
    await risk_svc.record_signal("CONSUMER", "cons-surat-100", "VELOCITY_NORMAL", "LOW", 5.0)
    risk_res = await risk_svc.evaluate_risk("cons-surat-100")
    assert risk_res["level"] == "LOW"

    audit_svc = AuditService()
    audit_event = await audit_svc.record("COMPLIANCE_EVALUATION_PASSED", "ord-surat-555", metadata=decision)
    assert audit_event["payload_hash"] is not None
