"""
Unit tests for FACCP Architectural Protocols 09-12 Suite.
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

from faccp_common.feature_flags import FeatureFlag, FeatureFlagRegistry, is_enabled
from scripts.constitution.check_domain_isolation import DomainIsolationChecker
from scripts.constitution.check_single_responsibility import SingleResponsibilityChecker
from scripts.constitution.check_shared_code import SharedCodeChecker


@pytest.mark.asyncio
async def test_feature_flag_evaluation():
    FeatureFlagRegistry.clear()
    
    flag = FeatureFlag(
        name="test_new_checkout",
        default=False,
        rollout_percentage=50,
        allowed_user_ids=["user_admin_123"],
        allowed_tenants=["tenant_alpha"],
    )
    FeatureFlagRegistry.register(flag)

    # Allowlist checks
    assert await is_enabled("test_new_checkout", {"user_id": "user_admin_123"}) is True
    assert await is_enabled("test_new_checkout", {"tenant_id": "tenant_alpha"}) is True

    # Deterministic rollout check
    val_1 = await is_enabled("test_new_checkout", {"user_id": "user_random_456"})
    val_2 = await is_enabled("test_new_checkout", {"user_id": "user_random_456"})
    assert val_1 == val_2  # Deterministic repeatability

    # Non-existent flag
    assert await is_enabled("non_existent_flag") is False


def test_domain_isolation_checker():
    checker = DomainIsolationChecker(root_dir=root_dir)
    report = checker.check_all()
    assert isinstance(report, dict)
    # Ensure no cross-domain import violations in repository
    assert len(report) == 0


def test_single_responsibility_checker():
    checker = SingleResponsibilityChecker(root_dir=root_dir)
    report = checker.check_all()
    assert isinstance(report, dict)
    assert len(report) == 0


def test_shared_code_checker():
    checker = SharedCodeChecker(root_dir=root_dir)
    violations = checker.check_common_dir()
    assert isinstance(violations, list)
    assert len(violations) == 0
