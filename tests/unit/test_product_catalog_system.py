"""
Unit tests for Master Product Catalog & Consumer View System Architecture auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_product_catalog_system import (
    ProductCatalogSystemChecker,
    PRODUCT_CATALOG_SYSTEM_MAP,
)


def test_product_catalog_system_auditor_report():
    checker = ProductCatalogSystemChecker(root_dir=root_dir)
    res = checker.audit_product_catalog_system()

    assert res["total_modules"] == 27
    assert res["verified_modules"] == 27
    assert res["score_pct"] == 100.0
    assert len(PRODUCT_CATALOG_SYSTEM_MAP) == 27

    # Test key modules across Product Master, Visibility Levels, View Composer, Action Model, and Events
    assert PRODUCT_CATALOG_SYSTEM_MAP["PRD-DOM-01"] == "Product Master Domain Separation (Master vs SKU vs Store Listing)"
    assert PRODUCT_CATALOG_SYSTEM_MAP["PRD-MOD-01"] == "Product Master Registry"
    assert PRODUCT_CATALOG_SYSTEM_MAP["PRD-VIS-00"] == "Visibility Level 0 - Public Access"
    assert PRODUCT_CATALOG_SYSTEM_MAP["PRD-VIS-03"] == "Visibility Level 3 - Transaction Eligible Consumer"
    assert PRODUCT_CATALOG_SYSTEM_MAP["PRD-VIS-05"] == "Visibility Level 5 - Administrative Governance View"
    assert PRODUCT_CATALOG_SYSTEM_MAP["PRD-CMP-01"] == "View Composer Engine & Projection Models"
    assert PRODUCT_CATALOG_SYSTEM_MAP["PRD-ACT-01"] == "Server-Authoritative Action Model (view, add_to_cart, purchase)"
    assert PRODUCT_CATALOG_SYSTEM_MAP["PRD-EVT-01"] == "Product Event Notifications (PRODUCT_CREATED, PRODUCT_APPROVED, etc.)"
