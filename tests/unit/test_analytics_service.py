"""
Unit tests for Phase 9 Analytics Service (Schemas, Metrics, Snapshots, and Static Checker).
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/analytics-service")
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

from app.schemas.analytics import MetricAggregateCreate, SnapshotGenerateRequest
from scripts.constitution.check_analytics_service import AnalyticsServiceChecker


def test_metric_aggregate_create_valid():
    now = datetime.now(timezone.utc)
    m = MetricAggregateCreate(
        metric_name="ORDER_VOLUME_1H",
        dimension_key="STORE_ID",
        dimension_value="STR_KA_BLR_001",
        metric_value=42.0,
        period_start=now - timedelta(hours=1),
        period_end=now,
    )
    assert m.metric_name == "ORDER_VOLUME_1H"
    assert m.metric_value == 42.0


def test_snapshot_generate_request_valid():
    req = SnapshotGenerateRequest(
        report_type="EXCISE_TAX",
        generated_by="auditor_101",
        snapshot_data={"tax_paid": 5000.0},
    )
    assert req.report_type == "EXCISE_TAX"


def test_analytics_service_checker():
    checker = AnalyticsServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
