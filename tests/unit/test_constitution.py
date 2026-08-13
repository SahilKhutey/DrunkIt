"""
Unit tests for FACCP Fundamental Development Protocols & Constitution Suite.
"""

from __future__ import annotations

import os
import sys
import pytest

# Add services/_common to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from faccp_common.security import SecurityStandard, PasswordPolicy, TokenStandards
from faccp_common.privacy import DataMinimizationPolicy, ConsentPolicy, RetentionPolicy
from faccp_common.compliance import PolicyAccessGuard
from faccp_common.dto import SuccessResponse, ErrorResponse, PaginatedResponse, PageInfo
from scripts.constitution.check_compliance import ConstitutionChecker


def test_security_standard_allowlist_and_mfa():
    assert "/health" in SecurityStandard.PUBLIC_ROUTES_ALLOWLIST
    assert SecurityStandard.requires_mfa("SUPER_ADMIN", "read") is True
    assert SecurityStandard.requires_mfa("CONSUMER", "approve") is True
    assert SecurityStandard.requires_mfa("CONSUMER", "read") is False
    assert SecurityStandard.mfa_max_age_seconds() == 900


def test_password_policy_validation():
    valid, msg = PasswordPolicy.validate("ValidP@ssw0rd123!")
    assert valid is True
    assert msg == ""

    valid_short, msg_short = PasswordPolicy.validate("Short1!")
    assert valid_short is False
    assert "at least 12 characters" in msg_short

    valid_email, msg_email = PasswordPolicy.validate("P@ssw0rd123!john", user_email="john@example.com")
    assert valid_email is False
    assert "username" in msg_email


def test_data_minimization_filter():
    consumer_data = {
        "consumer_id": "c-123",
        "consumer_level": "C3",
        "age_eligible": True,
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone": "+1234567890",
    }
    
    order_data = DataMinimizationPolicy.filter_for_service(consumer_data, "order-service")
    assert "consumer_id" in order_data
    assert "email" not in order_data
    assert "phone" not in order_data

    delivery_data = DataMinimizationPolicy.filter_for_service(consumer_data, "delivery-service")
    assert "phone" in delivery_data
    assert "email" not in delivery_data


def test_policy_access_guard_audit():
    clean_code = "def get_consumer(): return db.query(Consumer).all()"
    violations_clean = PolicyAccessGuard.audit("services/order-service/app/main.py", clean_code)
    assert len(violations_clean) == 0

    dirty_code = "if user.age >= 21:\n    allow_sale()"
    violations_dirty = PolicyAccessGuard.audit("services/order-service/app/main.py", dirty_code)
    assert len(violations_dirty) > 0


def test_dto_envelope_serialization():
    resp = SuccessResponse(data={"order_id": "ord-123"}, message="Order fetched")
    assert resp.success is True
    assert resp.data["order_id"] == "ord-123"

    page_info = PageInfo(
        total_items=100, page=1, page_size=10, total_pages=10, has_next=True, has_previous=False
    )
    paginated = PaginatedResponse(items=[{"id": 1}], page_info=page_info)
    assert paginated.success is True
    assert paginated.page_info.total_items == 100


def test_constitution_checker_execution():
    checker = ConstitutionChecker(root_dir=root_dir)
    report = checker.check_all()
    assert report["total_articles"] == 50
    assert report["passed"] == 50



    assert "compliance_score_pct" in report




















