"""
Unit tests for Phase 8 Risk Service (Schemas, Fraud Scoring, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/risk-service")
common_path = os.path.join(root_dir, "services/_common")

for mod_name in list(sys.modules.keys()):
    if mod_name == "app" or mod_name.startswith("app."):
        del sys.modules[mod_name]

if service_path not in sys.path:
    sys.path.insert(0, service_path)
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.schemas.risk import RiskEvaluationRequest, FraudRuleCreate
from scripts.constitution.check_risk_service import RiskServiceChecker


def test_risk_evaluation_request_valid():
    req = RiskEvaluationRequest(
        entity_type="ORDER",
        entity_id="ORD-20260812-9A8B",
        amount_inr=30000.0,
        velocity_count_1h=4,
        is_new_device=True,
    )
    assert req.entity_type == "ORDER"
    assert req.amount_inr == 30000.0


def test_fraud_rule_create_valid():
    rule = FraudRuleCreate(
        rule_name="RULE_HIGH_VELOCITY",
        description="High frequency order attempts",
        risk_score_impact=0.40,
    )
    assert rule.rule_name == "RULE_HIGH_VELOCITY"


def test_risk_service_checker():
    checker = RiskServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
