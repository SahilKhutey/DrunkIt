"""
Unit tests for Catalog & Template Platform Architecture (4 Layers, 18 Sub-Catalogs, 7 Golden Templates).
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

from faccp_common.catalog import (
    CatalogRegistry, CatalogLayer, CatalogObject, CatalogLifecycleState,
    CatalogValidationEngine, GoldenTemplateRegistry
)
from scripts.constitution.check_catalog_and_templates import CatalogAndTemplatesChecker


def test_catalog_sub_catalog_counts():
    assert len(CatalogRegistry.ADMIN_SUB_CATALOGS) == 10
    assert len(CatalogRegistry.DEVELOPER_SUB_CATALOGS) == 8


def test_golden_templates_registry():
    assert len(GoldenTemplateRegistry.TEMPLATES) == 7
    secure_api = GoldenTemplateRegistry.get_template("secure-api")
    assert secure_api.requires_arch_review is True


def test_catalog_validation_engine():
    engine = CatalogValidationEngine()
    obj = CatalogObject(
        object_id="svc_order",
        name="Order Service",
        layer=CatalogLayer.DEVELOPER,
        sub_catalog="DEV-CAT-01 Service Catalog",
        state=CatalogLifecycleState.ACTIVE,
    )

    result = engine.validate(obj)
    assert result.is_valid is True
    assert len(result.stages_passed) == 7


def test_catalog_and_templates_checker():
    checker = CatalogAndTemplatesChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
