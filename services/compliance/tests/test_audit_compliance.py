import pytest
from services.compliance.app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_audit_recording_with_hash():
    svc = AuditService()
    event = await svc.record(
        action="DECISION_EVALUATED",
        subject_id="order-audit-100",
        metadata={"decision": "ALLOW"},
    )

    assert event["event_type"] == "DECISION_EVALUATED"
    assert event["payload_hash"] is not None
    assert len(event["payload_hash"]) == 64
