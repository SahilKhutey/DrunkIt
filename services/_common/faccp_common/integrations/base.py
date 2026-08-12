"""
Base integration adapter and registry.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from faccp_common.exceptions import IntegrationError
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger

logger = get_logger(__name__)


@dataclass
class IntegrationConfig:
    name: str
    enabled: bool = True
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_base_delay: float = 1.0
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_seconds: float = 30.0


class IntegrationAdapter(ABC):

    def __init__(self, config: IntegrationConfig, producer: EventProducer | None = None) -> None:
        self.config = config
        self.producer = producer
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._is_open = False

    @abstractmethod
    async def health_check(self) -> bool:
        ...

    async def call_with_retry(self, func, *args, **kwargs) -> Any:
        if not self.config.enabled:
            raise IntegrationError(f"Integration {self.config.name} is disabled")
        if self._is_open:
            if self._last_failure_time and (time.time() - self._last_failure_time) > self.config.circuit_breaker_recovery_seconds:
                self._is_open = False
                self._failure_count = 0
                logger.info("integration.circuit_closed", name=self.config.name)
            else:
                raise IntegrationError(f"Integration {self.config.name} circuit breaker is OPEN")
        last_exc = None
        for attempt in range(self.config.max_retries):
            try:
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=self.config.timeout_seconds
                )
                if attempt > 0:
                    logger.info("integration.retry_succeeded", name=self.config.name, attempt=attempt)
                if self._failure_count > 0:
                    self._failure_count = 0
                return result
            except Exception as e:
                last_exc = e
                self._failure_count += 1
                if self._failure_count >= self.config.circuit_breaker_failure_threshold:
                    self._is_open = True
                    self._last_failure_time = time.time()
                    logger.warning("integration.circuit_opened", name=self.config.name, error=str(e))
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_base_delay * (2 ** attempt)
                    logger.warning(
                        "integration.retry", name=self.config.name, attempt=attempt,
                        error=str(e), delay=delay,
                    )
                    await asyncio.sleep(delay)
        raise IntegrationError(f"Integration {self.config.name} failed after {self.config.max_retries} retries: {last_exc}")


class IntegrationRegistry:

    def __init__(self) -> None:
        self._adapters: dict[str, IntegrationAdapter] = {}

    def register(self, name: str, adapter: IntegrationAdapter) -> None:
        self._adapters[name] = adapter

    def get(self, name: str) -> IntegrationAdapter:
        if name not in self._adapters:
            raise KeyError(f"Integration not registered: {name}")
        return self._adapters[name]

    def list(self) -> list[str]:
        return list(self._adapters.keys())

    async def health_check_all(self) -> dict[str, bool]:
        results = {}
        for name, adapter in self._adapters.items():
            try:
                results[name] = await adapter.health_check()
            except Exception:
                results[name] = False
        return results
