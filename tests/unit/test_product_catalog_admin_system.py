"""
Unit tests for Master User/Admin Product Catalog & Listing Template System Architecture auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_product_catalog_admin import (
    ProductCatalogAdminChecker,
    PRODUCT_CATALOG_ADMIN_MAP,
)


def test_product_catalog_admin_system_auditor_report():
    checker = ProductCatalogAdminChecker(root_dir=root_dir)
    res = checker.audit_product_catalog_admin()

    assert res["total_modules"] == 18
    assert res["verified_modules"] == 18
    assert res["score_pct"] == 100.0
    assert len(PRODUCT_CATALOG_ADMIN_MAP) == 18


    # Test key modules across Wizard, Soft-Delete, Dependency Check, Template Builder, and APIs
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-WIZ-01"] == "Step 1 - Product Identity Setup"
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-WIZ-03"] == "Step 3 - Dynamic Attribute Template Hydration"
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-WIZ-05"] == "Step 5 - Regulatory Compliance & Documentation Isolation"
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-WIZ-10"] == "Step 10 - Catalog State Publish & Event Dispatch"
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-DEL-01"] == "Soft-Delete Policy (ACTIVE -> SUSPENDED -> ARCHIVED)"
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-DEP-01"] == "Product Dependency Check Engine (Listings, Orders, Financial Audit)"
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-TPL-01"] == "Low-Code Listing Template Builder (Fields, Layout, Validation Rules)"
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-BULK-01"] == "Bulk Import/Export Pipeline (Parse -> Validate -> Preview -> Commit)"
    assert PRODUCT_CATALOG_ADMIN_MAP["ADM-API-01"] == "Admin Control Plane APIs (/admin/products, /admin/listing-templates)"
