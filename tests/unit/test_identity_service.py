"""
Unit tests for Phase 1 Identity Service (Schemas, Validation, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/identity-service")
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

from app.schemas.auth import RegisterRequest, LoginRequest, PasswordChangeRequest
from scripts.constitution.check_identity_service import IdentityServiceChecker



def test_register_request_valid():
    req = RegisterRequest(
        email="testuser@faccp.com",
        password="SecurePassword123!",
        primary_role="CONSUMER",
    )
    assert req.email == "testuser@faccp.com"
    assert req.primary_role == "CONSUMER"


def test_register_request_invalid_password():
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="testuser@faccp.com",
            password="weakpassword",
            primary_role="CONSUMER",
        )


def test_login_request_valid():
    req = LoginRequest(
        email="admin@faccp.com",
        password="AdminPassword123!",
    )
    assert req.email == "admin@faccp.com"



def test_identity_service_checker():
    checker = IdentityServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
