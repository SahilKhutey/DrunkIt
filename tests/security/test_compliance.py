"""Unit tests for Compliance Engine evaluation and policy decision versioning."""

from dataclasses import dataclass
import pytest
from faccp_platform.compliance.engine import ComplianceEngine
from faccp_platform.compliance.rules import AgeVerificationRule, EligibilityRule


@dataclass
class SampleContext:
    eligible: bool = True
    age_verified: bool = True


def test_compliance_engine_approved():
    """Verify eligible consumer decision is approved with recorded policy version."""
    engine = ComplianceEngine()
    ctx = SampleContext(eligible=True, age_verified=True)
    decision = engine.evaluate(ctx)

    assert decision.allowed is True
    assert decision.state == "verified"
    assert decision.policy_version == "2026.08"
    assert len(decision.reasons) == 0


def test_compliance_engine_rejected():
    """Verify ineligible consumer decision is rejected with specific failure reason."""
    engine = ComplianceEngine()
    ctx = SampleContext(eligible=False, age_verified=True)
    decision = engine.evaluate(ctx)

    assert decision.allowed is False
    assert decision.state == "rejected"
    assert "eligibility_failed" in decision.reasons
