"""
Unit tests for Protocols 15, 16, & 17 (Authentication, Authorization, & Trust Verification).
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

from faccp_common.auth import (
    create_access_token, validate_access_token, TokenExtractor,
    AuthenticationPipeline, RefreshTokenRotation, MFAEnforcement, SessionPolicy
)
from faccp_common.authz import (
    RBACEngine, ResourceOwnershipChecker, JurisdictionAuthZ,
    OrganizationAuthZ, StoreAuthZ, PolicyAuthZ, AuthorizationEngine
)
from faccp_common.trust import TrustDecisionEngine, TrustOutcome, TrustThresholds
from scripts.constitution.check_auth_pipeline import AuthPipelineChecker


def test_token_creation_and_validation():
    token, jti = create_access_token(
        user_id="usr_999",
        roles=["CONSUMER"],
        primary_role="CONSUMER",
        consumer_level="C3_AGE_ELIGIBLE",
        trust_score=85,
    )
    assert len(token) > 30
    assert len(jti) > 20

    claims = validate_access_token(token)
    assert claims["sub"] == "usr_999"
    assert claims["consumer_level"] == "C3_AGE_ELIGIBLE"
    assert claims["trust_score"] == 85


def test_authentication_pipeline():
    token, _ = create_access_token("u1", ["CONSUMER"], "CONSUMER")
    pipeline = AuthenticationPipeline()
    context = pipeline.authenticate_token(token)
    assert context.user_id == "u1"
    assert context.primary_role == "CONSUMER"


def test_refresh_token_rotation():
    rotation = RefreshTokenRotation()
    family_id = "fam_1"
    new_token = rotation.rotate_token("jti_1", family_id)
    assert len(new_token) > 10

    # Replay attack raises RuntimeError
    with pytest.raises(RuntimeError):
        rotation.rotate_token("jti_1", family_id)


def test_mfa_enforcement():
    assert MFAEnforcement.requires_mfa("SUPER_ADMIN", "order:read") is True
    assert MFAEnforcement.requires_fresh_mfa("CONSUMER", "mfa:disable") is True


@pytest.mark.asyncio
async def test_authorization_engine_pipeline():
    token, _ = create_access_token(
        user_id="u1",
        roles=["SUPER_ADMIN"],
        primary_role="SUPER_ADMIN",
        assigned_jurisdictions=["IN-KA"],
    )
    context = AuthenticationPipeline().authenticate_token(token)
    engine = AuthorizationEngine()

    decision = await engine.authorize(
        actor=context,
        action="order:read",
        resource_type="order",
        resource_id="ord_1",
        resource_attrs={"jurisdiction_code": "IN-KA"},
    )
    assert decision.effect == "PERMIT"
    assert "rbac" in decision.checks_passed


@pytest.mark.asyncio
async def test_trust_decision_engine():
    token, _ = create_access_token(
        user_id="u1",
        roles=["CONSUMER"],
        primary_role="CONSUMER",
        consumer_level="C3_AGE_ELIGIBLE",
        trust_score=90,
    )
    context = AuthenticationPipeline().authenticate_token(token)
    trust_engine = TrustDecisionEngine()

    decision = await trust_engine.evaluate(
        actor=context,
        action="order:create",
        resource={"product_type": "alcohol", "license": {"status": "ACTIVE"}},
        context={"amount": 2000},
    )
    assert decision.outcome == TrustOutcome.ALLOW
    assert decision.confidence > 0.8


def test_auth_pipeline_checker():
    checker = AuthPipelineChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
