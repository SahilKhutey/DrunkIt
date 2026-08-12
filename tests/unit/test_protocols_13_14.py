"""
Unit tests for FACCP Protocols 13 & 14 (Source-of-Truth & Identity Protocol).
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from faccp_common.governance import SourceOfTruthRegistry, SourceOfTruthResolver, DataSharingPolicy
from faccp_common.identity import (
    ActorType, Identity, TrustStatus, AnonymousAccessGuard, ServiceIdentity,
    ConsumerTrustLevel, SENSITIVE_OPERATIONS
)
from faccp_common.exceptions import UnauthorizedError
from scripts.constitution.check_source_of_truth import SourceOfTruthChecker
from scripts.constitution.check_identity_compliance import IdentityComplianceChecker


def test_source_of_truth_registry():
    owner, table = SourceOfTruthRegistry.get_owner("order")
    assert owner == "order-service"
    assert table == "orders table"

    owner_cons, _ = SourceOfTruthRegistry.get_owner("consumer_profile")
    assert owner_cons == "consumer-service"

    with pytest.raises(ValueError):
        SourceOfTruthRegistry.get_owner("invalid_domain_item")


def test_source_of_truth_resolver_and_data_sharing():
    # Resolver source wins
    resolved = SourceOfTruthResolver.resolve_conflict("projection_val", "source_val", "level")
    assert resolved == "source_val"

    # Data sharing policy filter
    raw_consumer = {
        "consumer_id": "c-1",
        "consumer_level": "C3",
        "age_eligible": True,
        "first_name": "Bob",
    }
    filtered = DataSharingPolicy.filter_for_recipient(raw_consumer, "ORDER", "CONSUMER")
    assert "consumer_id" in filtered
    assert "first_name" not in filtered


def test_identity_and_trust_status():
    identity = Identity(
        actor_id="usr-123",
        actor_type=ActorType.CONSUMER,
        primary_identifier="user@example.com",
        display_name="User Test",
        roles=["CONSUMER"],
    )
    assert identity.actor_type == ActorType.CONSUMER

    trust = TrustStatus(actor_id="usr-123", actor_type=ActorType.CONSUMER, base_score=80, risk_score=10)
    assert trust.effective_trust_score == 70
    assert trust.trust_level == "MEDIUM"
    assert trust.can_perform_sensitive_action() is True

    trust.block(reason="Suspicious behavior")
    assert trust.trust_level == "BLOCKED"
    assert trust.can_perform_sensitive_action() is False


def test_anonymous_access_guard():
    assert "order:create" in SENSITIVE_OPERATIONS

    # Anonymous access on sensitive action raises UnauthorizedError
    with pytest.raises(UnauthorizedError):
        AnonymousAccessGuard.require_authenticated(actor=None, action="order:create")

    # Active identity passes
    active_identity = Identity("u-1", ActorType.CONSUMER, "u@ex.com", "U", status="active")
    AnonymousAccessGuard.require_authenticated(actor=active_identity, action="order:create")


def test_service_identity_jwt():
    s_ident = ServiceIdentity(service_name="order-service", environment="test")
    token = s_ident.get_token()
    assert isinstance(token, str)
    assert len(token) > 20


def test_source_of_truth_checker():
    checker = SourceOfTruthChecker(root_dir=root_dir)
    report = checker.check_all()
    assert isinstance(report, dict)
    assert len(report) == 0


def test_identity_compliance_checker():
    checker = IdentityComplianceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert isinstance(report, dict)
    assert len(report) == 0
