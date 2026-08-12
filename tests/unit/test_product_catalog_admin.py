"""
Unit tests for Product Catalog Admin System Architecture (10 Wizard Steps, 12 Field Types, Admin vs Retailer Matrix).
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

from faccp_common.product_admin import (
    ProductWizardEngine, WizardStep, ProductCreationContext,
    ListingTemplateBuilder, FieldType, ListingTemplateState,
    AdminRetailerPermissionsMatrix, PermissionAction
)
from scripts.constitution.check_product_catalog_admin import ProductCatalogAdminChecker


def test_wizard_engine_steps():
    assert len(ProductWizardEngine.STEPS_ORDER) == 10
    ctx = ProductCreationContext(step=WizardStep.IDENTITY)
    engine = ProductWizardEngine()

    next_step = engine.advance_step(ctx)
    assert next_step == WizardStep.CLASSIFICATION


def test_listing_template_builder():
    builder = ListingTemplateBuilder(template_id="tpl_std", name="Standard Listing Template")
    assert builder.state == ListingTemplateState.DRAFT
    assert len(builder.FIELD_TYPES) == 12


def test_permissions_matrix():
    assert AdminRetailerPermissionsMatrix.can_admin(PermissionAction.CREATE_PRODUCT_MASTER) is True
    assert AdminRetailerPermissionsMatrix.can_retailer(PermissionAction.CREATE_PRODUCT_MASTER) is False
    assert AdminRetailerPermissionsMatrix.can_retailer(PermissionAction.SET_STORE_PRICE) is True


def test_product_catalog_admin_checker():
    checker = ProductCatalogAdminChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
