import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/audit-service")))

import pytest
from audit_app.main import AUDIT_LOG_STORE, record_event, verify_chain_integrity, AuditEventCreate

def test_hash_chain_linking():
    initial_length = len(AUDIT_LOG_STORE)
    last_hash_before = AUDIT_LOG_STORE[-1].current_hash

    req = AuditEventCreate(
        event_type="SOD_VIOLATION_CHECK",
        actor_id="SEC-ADM-01",
        actor_type="PLATFORM_ADMIN",
        action="EVALUATE_SOD",
        resource_id="RES-9901",
        resource_type="EXCISE_LICENSE",
        jurisdiction="IN-KA",
        payload={"result": "PASS"}
    )
    rec = record_event(req)

    assert rec.sequence_number == initial_length + 1
    assert rec.prev_hash == last_hash_before
    assert len(rec.current_hash) == 64

def test_audit_chain_integrity_valid():
    report = verify_chain_integrity()
    assert report.valid_chain is True
    assert report.total_events >= 2
    assert report.tampered_index is None

def test_audit_chain_tamper_detection():
    # Simulate unauthorized modification of historical event
    original_action = AUDIT_LOG_STORE[0].action
    AUDIT_LOG_STORE[0].action = "TAMPERED_UNAUTHORIZED_ACTION"

    report = verify_chain_integrity()
    assert report.valid_chain is False
    assert report.tampered_index == 0

    # Revert back to maintain clean state for remaining tests
    AUDIT_LOG_STORE[0].action = original_action
    report_reverted = verify_chain_integrity()
    assert report_reverted.valid_chain is True
