"""Service registry data models and Enums."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ServiceType(str, Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    WORKER = "worker"
    INFRASTRUCTURE = "infrastructure"


class RuntimeType(str, Enum):
    PYTHON = "python"
    NODE = "node"
    DOCKER = "docker"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class HealthConfig:
    path: str = "/health"


@dataclass(frozen=True)
class ServiceDefinition:
    name: str
    type: ServiceType
    runtime: RuntimeType
    host: str
    port: int

    health: HealthConfig = field(default_factory=HealthConfig)
    readiness: HealthConfig = field(default_factory=lambda: HealthConfig("/ready"))
    dependencies: tuple[str, ...] = ()

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        return f"{self.base_url}{self.health.path}"

    @property
    def readiness_url(self) -> str:
        return f"{self.base_url}{self.readiness.path}"
