"""
Unit tests for Phase 11 API Gateway Service (Schemas, Routes, Health, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/api-gateway")
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

from app.schemas.gateway import ServiceRouteInfo, GatewayHealthSummary
from app.services.gateway_service import GatewayService
from scripts.constitution.check_gateway_service import GatewayServiceChecker


def test_service_route_info_valid():
    r = ServiceRouteInfo(service_name="identity", target_url="http://localhost:8001")
    assert r.service_name == "identity"


def test_gateway_service_routes():
    svc = GatewayService()
    routes = svc.get_routes()
    assert len(routes) >= 14


def test_gateway_service_checker():
    checker = GatewayServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
