"""
Multi-region management and routing.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

from faccp_common.logging import get_logger

logger = get_logger(__name__)


class RegionStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNREACHABLE = "UNREACHABLE"
    INITIALIZING = "INITIALIZING"


@dataclass
class Region:
    code: str
    name: str
    endpoint: str
    is_primary: bool = False
    priority: int = 100
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RegionHealth:
    region_code: str
    status: RegionStatus
    latency_ms: float
    last_checked: float
    error: str | None = None
    checks: dict[str, bool] = field(default_factory=dict)


class RegionManager:

    def __init__(self, regions: list[Region], check_interval: float = 10.0) -> None:
        self.regions: dict[str, Region] = {r.code: r for r in regions}
        self.check_interval = check_interval
        self.health: dict[str, RegionHealth] = {}
        self._http: httpx.AsyncClient | None = None
        self._running = False

    async def start(self) -> None:
        self._http = httpx.AsyncClient(timeout=5.0)
        self._running = True
        await self.check_all()
        asyncio.create_task(self._health_check_loop())

    async def stop(self) -> None:
        self._running = False
        if self._http:
            await self._http.aclose()

    async def _health_check_loop(self) -> None:
        while self._running:
            try:
                await self.check_all()
            except Exception:
                logger.exception("health_check_loop_failed")
            await asyncio.sleep(self.check_interval)

    async def check_all(self) -> dict[str, RegionHealth]:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=5.0)
        results: dict[str, RegionHealth] = {}
        tasks = [self._check_region(r) for r in self.regions.values()]
        for coro in asyncio.as_completed(tasks):
            try:
                health = await coro
                results[health.region_code] = health
            except Exception:
                logger.exception("region_check_failed")
        self.health = results
        return results

    async def _check_region(self, region: Region) -> RegionHealth:
        start = time.perf_counter()
        checks = {}
        error = None
        try:
            response = await self._http.get(f"{region.endpoint}/health", timeout=3.0)
            checks["health"] = response.status_code == 200
        except Exception as e:
            checks["health"] = False
            error = str(e)

        try:
            response = await self._http.get(f"{region.endpoint}/health/db", timeout=3.0)
            checks["database"] = response.status_code == 200
        except Exception:
            checks["database"] = False

        try:
            response = await self._http.get(f"{region.endpoint}/health/kafka", timeout=3.0)
            checks["kafka"] = response.status_code == 200
        except Exception:
            checks["kafka"] = False

        latency_ms = (time.perf_counter() - start) * 1000
        all_ok = all(checks.values())
        if all_ok and latency_ms < 500:
            status = RegionStatus.HEALTHY
        elif all_ok and latency_ms < 2000:
            status = RegionStatus.DEGRADED
        else:
            status = RegionStatus.UNREACHABLE

        return RegionHealth(
            region_code=region.code, status=status,
            latency_ms=latency_ms, last_checked=time.time(),
            error=error, checks=checks,
        )

    def get_healthy_regions(self) -> list[Region]:
        return [
            r for r in self.regions.values()
            if self.health.get(r.code, RegionHealth(r.code, RegionStatus.HEALTHY, 0, 0)).status
            in (RegionStatus.HEALTHY, RegionStatus.DEGRADED)
        ]

    def get_preferred_region(self, request_context: dict[str, Any] | None = None) -> Region:
        request_context = request_context or {}
        preferred = request_context.get("preferred_region")
        if preferred and preferred in self.regions:
            return self.regions[preferred]

        client_country = request_context.get("client_country")
        if client_country:
            for r in self.regions.values():
                if r.metadata.get("country") == client_country:
                    if self.health.get(r.code, RegionHealth(r.code, RegionStatus.HEALTHY, 0, 0)).status == RegionStatus.HEALTHY:
                        return r

        healthy = self.get_healthy_regions()
        if healthy:
            def sort_key(r: Region) -> tuple[float, int]:
                h = self.health.get(r.code)
                latency = h.latency_ms if h else 9999
                return (latency, r.priority)
            return min(healthy, key=sort_key)

        for r in self.regions.values():
            if r.is_primary:
                return r
        return next(iter(self.regions.values()))
