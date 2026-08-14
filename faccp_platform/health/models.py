"""Health status models and Enums."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthResult:
    name: str
    status: HealthStatus
    latency_ms: float | None = None
    error: str | None = None

    @property
    def healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY
