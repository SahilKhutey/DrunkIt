"""
Unit tests for Phase 0 Foundation Execution (Identity, TokenValidator, AuthorizationEngine, EventEnvelope, TopicRegistry).
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

from faccp_common.trust import (
    Identity, ActorType, TokenValidator, create_access_token,
    AuthorizationEngine, AccessRequest, SubjectAttributes, ResourceAttributes, ActionAttributes, EnvironmentAttributes,
    default_authorization_engine, Role, Permission
)
from faccp_common.communication import EventEnvelope, create_envelope, TopicRegistry
from scripts.constitution.check_phase0_foundation import Phase0FoundationChecker


def test_identity_and_jwt_tokens():
    ident = Identity(
        actor_id="usr_admin_100",
        actor_type=ActorType.ADMIN,
        primary_identifier="admin@faccp.local",
        display_name="Super Admin",
        roles=["SUPER_ADMIN"],
    )
    jwt_secret = "test-secret-key-for-unit-tests-1234567890"
    token, jti = create_access_token(ident, jwt_secret=jwt_secret)

    validator = TokenValidator(jwt_secret=jwt_secret)
    res = validator.validate_access_token(token)
    assert res.valid is True
    assert res.claims["sub"] == "usr_admin_100"


def test_authorization_engine():
    engine = default_authorization_engine()
    req = AccessRequest(
        subject=SubjectAttributes(user_id="usr_consumer", primary_role="CONSUMER", roles=["CONSUMER"]),
        resource=ResourceAttributes(resource_type="order", resource_id="ord_100"),
        action=ActionAttributes(action="create"),
        environment=EnvironmentAttributes(),
    )
    decision = engine.evaluate(req)
    assert decision.is_permit is True


def test_event_envelope_creation():
    env = create_envelope(
        event_type="identity.created",
        payload={"user_id": "usr_100"},
        producer="identity-service",
    )
    assert env.event_type == "identity.created"
    assert env.metadata.producer == "identity-service"
    assert len(TopicRegistry.all_names()) >= 12


def test_phase0_foundation_checker():
    checker = Phase0FoundationChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
