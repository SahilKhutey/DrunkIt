import pytest
from services.governance.app.engine.audit_engine import AuditEngine


@pytest.mark.asyncio
async def test_audit_chain_and_verification():
    engine = AuditEngine()
    e1 = await engine.record({"event_type": "order.created", "action": "CREATE", "subject_id": "ord-101"})
    e2 = await engine.record({"event_type": "payment.authorized", "action": "PAY", "subject_id": "ord-101"})

    assert e1["sequence_number"] == 1001
    assert e2["sequence_number"] == 1002
    assert e2["previous_hash"] == e1["event_hash"]

    valid = await engine.verify_chain()
    assert valid is True
