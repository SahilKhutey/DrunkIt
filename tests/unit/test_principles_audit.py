import pytest
from faccp_common.principles_audit import PrinciplesAuditEngine


def test_principles_audit_engine():
    engine = PrinciplesAuditEngine()
    audit_report = engine.audit_all()

    assert audit_report["total_principles"] == 30
    assert audit_report["passed"] == 30
    assert audit_report["failed"] == 0
    assert audit_report["compliance_score_pct"] == 100.0
    assert len(audit_report["results"]) == 30
