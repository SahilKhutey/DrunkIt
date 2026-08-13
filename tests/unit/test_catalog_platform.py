"""
Unit tests for Master Catalog & Template System Architecture auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_catalog_platform import (
    CatalogPlatformChecker,
    CATALOG_PLATFORM_MAP,
)


def test_catalog_platform_auditor_report():
    checker = CatalogPlatformChecker(root_dir=root_dir)
    res = checker.audit_catalog_platform()

    assert res["total_components"] == 36
    assert res["verified_components"] == 36
    assert res["score_pct"] == 100.0
    assert len(CATALOG_PLATFORM_MAP) == 36


    # Test key components across Administrative, Developer, Template, and Governance Catalogs
    assert CATALOG_PLATFORM_MAP["ADM-CAT-01"] == "Organization Catalog"
    assert CATALOG_PLATFORM_MAP["ADM-CAT-02"] == "Jurisdiction Catalog"
    assert CATALOG_PLATFORM_MAP["DEV-CAT-01"] == "Backend Service Catalog"
    assert CATALOG_PLATFORM_MAP["DEV-CAT-02"] == "Central API Registry & OpenAPI Schemas"
    assert CATALOG_PLATFORM_MAP["TPL-01"] == "Base Service Generator Template"
    assert CATALOG_PLATFORM_MAP["TPL-02"] == "FastAPI Service Boilerplate Template"
    assert CATALOG_PLATFORM_MAP["TPL-03"] == "Next.js Frontend Application Template"
    assert CATALOG_PLATFORM_MAP["GOV-01"] == "Catalog Lifecycle State Machine (DRAFT -> ACTIVE -> ARCHIVED)"
    assert CATALOG_PLATFORM_MAP["GOV-03"] == "Internal Developer Portal Registry"
    assert CATALOG_PLATFORM_MAP["GOV-06"] == "Golden Templates Repository & Architecture Review"
