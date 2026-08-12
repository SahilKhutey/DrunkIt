"""
Unit tests for Phase 8 Audit Service (Schemas, Validation, Hash Chain Calculation, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/audit-service")
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

from app.schemas.audit import AuditEntryCreate
from app.services.audit_service import compute_hash, GENESIS_HASH
from scripts.constitution.check_audit_service import AuditServiceChecker


def test_audit_entry_create_valid():
    entry = AuditEntryCreate(
        event_type="order.created",
        actor_id="usr_consumer_101",
        actor_role="CONSUMER",
        resource_type="ORDER",
        resource_id="ORD-20260812-9A8B",
        payload_json='{"amount": 2850.0}',
    )
    assert entry.event_type == "order.created"


def test_hash_calculation():
    h1 = compute_hash(GENESIS_HASH, "order.created", "usr_101", "ORD_001", "{}")
    h2 = compute_hash(GENESIS_HASH, "order.created", "usr_101", "ORD_001", "{}")
    assert h1 == h2
    assert len(h1) == 64  # SHA256 hex length


def test_audit_service_checker():
    checker = AuditServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
