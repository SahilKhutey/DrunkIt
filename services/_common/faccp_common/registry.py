"""Machine-readable service registry loader and helper methods."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ServiceEntry(BaseModel):
    name: str
    port: int
    directory: str
    database: Optional[str] = None
    health_path: str = "/health"
    ready_path: str = "/ready"
    tier: str = "core"
    dependencies: List[str] = Field(default_factory=list)


class ServiceRegistry(BaseModel):
    version: str = "1.0.0"
    updated_at: str = "2026-08-14"
    services: Dict[str, ServiceEntry]

    def get_service(self, key: str) -> Optional[ServiceEntry]:
        return self.services.get(key)

    def get_golden_path_services(self) -> List[ServiceEntry]:
        return [s for s in self.services.values() if s.tier == "golden_path"]

    def get_gateway_routes(self) -> Dict[str, str]:
        return {
            key: f"http://localhost:{srv.port}"
            for key, srv in self.services.items()
            if key != "api-gateway"
        }


_registry_cache: Optional[ServiceRegistry] = None


def find_registry_file() -> Path:
    """Find services.json by searching upwards from current or known project roots."""
    candidates = [
        Path.cwd() / "services" / "services.json",
        Path.cwd() / "services.json",
        Path(__file__).resolve().parents[2] / "services.json",
        Path(__file__).resolve().parents[3] / "services" / "services.json",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    raise FileNotFoundError("Could not locate services/services.json in workspace")


def load_registry(force_reload: bool = False) -> ServiceRegistry:
    global _registry_cache
    if _registry_cache is not None and not force_reload:
        return _registry_cache

    path = find_registry_file()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    _registry_cache = ServiceRegistry.model_validate(data)
    return _registry_cache
