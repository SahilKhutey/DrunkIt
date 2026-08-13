"""
Unit tests for Master Phase D5 Production Data & Real-Time Infrastructure auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_production_infrastructure import (
    ProductionInfrastructureChecker,
    PRODUCTION_INFRASTRUCTURE_MAP,
)


def test_production_infrastructure_auditor_report():
    checker = ProductionInfrastructureChecker(root_dir=root_dir)
    res = checker.audit_production_infrastructure()

    assert res["total_modules"] == 10
    assert res["verified_modules"] == 10
    assert res["score_pct"] == 100.0
    assert len(PRODUCTION_INFRASTRUCTURE_MAP) == 10

    # Test key modules
    assert PRODUCTION_INFRASTRUCTURE_MAP["INF-D5-01"] == "PostgreSQL & PostGIS Database Extensions (postgis, pgcrypto in init.sql)"
    assert PRODUCTION_INFRASTRUCTURE_MAP["INF-D5-03"] == "Transactional Outbox Event Model (OutboxEvent ORM model)"
    assert PRODUCTION_INFRASTRUCTURE_MAP["INF-D5-05"] == "Event Types Registry & Transactional Enqueue Publisher (EventType, enqueue_event)"
    assert PRODUCTION_INFRASTRUCTURE_MAP["INF-D5-07"] == "Redis Client & RedisKey Convention Builder (RedisKey: driver_location, driver_status, idempotency, delivery)"
    assert PRODUCTION_INFRASTRUCTURE_MAP["INF-D5-09"] == "API Request Idempotency Deduplication Service (IdempotencyService get/save)"
    assert PRODUCTION_INFRASTRUCTURE_MAP["INF-D5-10"] == "Immutable Operational Audit Log System (AuditLog, record_audit)"
