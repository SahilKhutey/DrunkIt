"""
Unit tests for Phase 2 Compliance Service (Schemas, Validation, and Static Checker).
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, time, timezone
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/compliance-service")
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

from app.schemas.compliance import PolicyCreate, ComplianceEvaluationRequest
from scripts.constitution.check_compliance_service import ComplianceServiceChecker



def test_policy_create_valid():
    p = PolicyCreate(
        code="POL_KA_TEST_2026",
        title="Karnataka Test Policy",
        jurisdiction="IN-KA",
        effective_from=datetime.now(timezone.utc),
        min_purchasing_age=21,
        max_volume_per_transaction_ml=4500,
        sales_start_time=time(10, 0),
        sales_end_time=time(22, 0),
    )
    assert p.code == "POL_KA_TEST_2026"
    assert p.min_purchasing_age == 21


def test_compliance_evaluation_request():
    req = ComplianceEvaluationRequest(
        reference_id="ref_eval_100",
        jurisdiction="IN-KA",
        actor_id="usr_consumer_1",
        consumer_age=22,
        total_volume_ml=1500,
    )
    assert req.reference_id == "ref_eval_100"
    assert req.consumer_age == 22


def test_compliance_service_checker():
    checker = ComplianceServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
