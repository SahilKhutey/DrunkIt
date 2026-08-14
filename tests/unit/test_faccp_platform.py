"""Unit test suite for faccp_platform Runtime Core."""

from __future__ import annotations

import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from faccp_platform.registry.models import (
    HealthConfig,
    RuntimeType,
    ServiceDefinition,
    ServiceType,
)
from faccp_platform.registry.loader import RegistryError, ServiceRegistry
from faccp_platform.health.models import HealthResult, HealthStatus
from faccp_platform.health.checks import check_tcp, check_service_port
from faccp_platform.runtime.service import create_service_app
from faccp_platform.config.settings import get_platform_settings


def test_service_definition_properties():
    def_service = ServiceDefinition(
        name="test-service",
        type=ServiceType.BACKEND,
        runtime=RuntimeType.PYTHON,
        host="localhost",
        port=8080,
    )
    assert def_service.base_url == "http://localhost:8080"
    assert def_service.health_url == "http://localhost:8080/health"
    assert def_service.readiness_url == "http://localhost:8080/ready"


def test_service_registry_loader_and_validation():
    registry_file = root_dir / "faccp_platform" / "registry" / "registry.yaml"
    registry = ServiceRegistry(registry_file)

    services = registry.services()
    assert len(services) > 0

    identity = registry.get("identity")
    assert identity.name == "identity"
    assert identity.port == 8001
    assert "postgres" in identity.dependencies

    errors = registry.validate()
    assert errors == []


def test_service_registry_unknown_service_raises():
    registry = ServiceRegistry()
    with pytest.raises(RegistryError):
        registry.get("non-existent-service-xyz")


def test_health_check_tcp_handles_closed_port():
    result = check_tcp("unbound-service", "localhost", 59999, timeout=0.2)
    assert result.healthy is False
    assert result.status == HealthStatus.UNHEALTHY
    assert result.error is not None


def test_create_service_app_endpoints():
    startup_called = []
    shutdown_called = []

    def on_startup():
        startup_called.append(True)

    def on_shutdown():
        shutdown_called.append(True)

    app = create_service_app(
        name="test-identity-service",
        version="0.2.0",
        startup_hooks=[on_startup],
        shutdown_hooks=[on_shutdown],
    )

    with TestClient(app) as client:
        assert startup_called == [True]

        res_health = client.get("/health")
        assert res_health.status_code == 200
        data_health = res_health.json()
        assert data_health["status"] == "healthy"
        assert data_health["service"] == "test-identity-service"
        assert data_health["version"] == "0.2.0"
        assert "timestamp" in data_health

        res_ready = client.get("/ready")
        assert res_ready.status_code == 200
        assert res_ready.json()["status"] == "ready"

        res_version = client.get("/version")
        assert res_version.status_code == 200
        assert res_version.json()["version"] == "0.2.0"

    assert shutdown_called == [True]
