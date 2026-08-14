"""Service registry YAML loader and validator."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

from .models import HealthConfig, RuntimeType, ServiceDefinition, ServiceType


class RegistryError(Exception):
    """Base exception for service registry errors."""
    pass


class ServiceRegistry:
    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            path = Path(__file__).resolve().parent / "registry.yaml"
        self.path = Path(path)
        self.data: dict[str, Any] = self._load_data()

    def _load_data(self) -> dict[str, Any]:
        if not self.path.exists():
            raise RegistryError(f"Registry file not found: {self.path}")
        with open(self.path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def services(self) -> tuple[ServiceDefinition, ...]:
        result: list[ServiceDefinition] = []
        raw_services = self.data.get("services", {})
        for key, config in raw_services.items():
            s_type = ServiceType(config.get("type", "backend"))
            r_type = RuntimeType(config.get("runtime", "python"))
            result.append(
                ServiceDefinition(
                    name=config.get("name", key),
                    type=s_type,
                    runtime=r_type,
                    host=config.get("host", "localhost"),
                    port=int(config.get("port", 8000)),
                    health=HealthConfig(
                        config.get("health", {}).get("path", "/health")
                    ),
                    readiness=HealthConfig(
                        config.get("readiness", {}).get("path", "/ready")
                    ),
                    dependencies=tuple(config.get("dependencies", [])),
                )
            )
        return tuple(result)

    def get(self, name: str) -> ServiceDefinition:
        for service in self.services():
            if service.name == name:
                return service
        raise RegistryError(f"Unknown service: {name}")

    def validate(self) -> list[str]:
        errors: list[str] = []
        services = {service.name: service for service in self.services()}
        ports: dict[int, str] = {}

        for service in services.values():
            if service.port in ports:
                errors.append(
                    f"Port collision: {service.name} and {ports[service.port]} both use {service.port}"
                )
            ports[service.port] = service.name

            for dependency in service.dependencies:
                if (
                    dependency not in services
                    and dependency not in self.data.get("infrastructure", {})
                ):
                    errors.append(
                        f"{service.name}: unknown dependency '{dependency}'"
                    )

        return errors
