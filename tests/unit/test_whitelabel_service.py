"""
Unit tests for Phase 12 Whitelabel Service (Schemas, Branding, Domains, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/whitelabel-service")
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

from app.schemas.whitelabel import TenantBrandingCreate, DomainBindingCreate
from scripts.constitution.check_whitelabel_service import WhitelabelServiceChecker


def test_tenant_branding_create_valid():
    b = TenantBrandingCreate(
        tenant_id="tenant_royal_wines",
        brand_name="Royal Spirits",
        primary_color_hex="#1a202c",
        secondary_color_hex="#d69e2e",
    )
    assert b.brand_name == "Royal Spirits"


def test_domain_binding_create_valid():
    d = DomainBindingCreate(
        tenant_id="tenant_royal_wines",
        domain_name="order.royalspirits.in",
    )
    assert d.domain_name == "order.royalspirits.in"


def test_whitelabel_service_checker():
    checker = WhitelabelServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
