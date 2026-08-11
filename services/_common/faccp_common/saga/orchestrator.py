"""
Saga pattern implementation for distributed transactions.
Each Saga is a sequence of steps with compensations. If a step fails, previous steps are compensated in reverse order.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable

from faccp_common.events import make_event
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger

logger = get_logger(__name__)


class SagaState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPENSATING = "COMPENSATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATED = "COMPENSATED"


@dataclass
class CompensationAction:
    """A compensation for a previously completed step."""
    name: str
    func: Callable[..., Awaitable[Any]]
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class SagaStep:
    """A single step in a saga."""
    name: str
    action: Callable[..., Awaitable[Any]]
    compensation: CompensationAction | None = None
    timeout_seconds: float = 30.0
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class Saga:
    """A distributed transaction composed of steps."""
    saga_id: str = field(default_factory=lambda: f"saga_{uuid.uuid4().hex[:16]}")
    name: str = ""
    state: SagaState = SagaState.PENDING
    steps: list[SagaStep] = field(default_factory=list)
    completed_steps: list[str] = field(default_factory=list)
    failed_step: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)


class SagaOrchestrator:

    def __init__(self, producer: EventProducer | None = None) -> None:
        self.producer = producer
        self._active: dict[str, Saga] = {}

    async def execute(self, saga: Saga) -> Saga:
        saga.state = SagaState.RUNNING
        saga.started_at = datetime.now(timezone.utc)
        self._active[saga.saga_id] = saga
        self._log(saga, "saga.started")

        try:
            for i, step in enumerate(saga.steps):
                saga.context["_current_step"] = step.name
                self._log(saga, f"step.starting: {step.name}")
                try:
                    result = await asyncio.wait_for(
                        step.action(saga.context), timeout=step.timeout_seconds
                    )
                    saga.context[f"step_{step.name}_result"] = result
                    saga.completed_steps.append(step.name)
                    self._log(saga, f"step.completed: {step.name}")
                except Exception as e:
                    saga.failed_step = step.name
                    saga.error = str(e)
                    self._log(saga, f"step.failed: {step.name}: {e}")
                    await self._compensate(saga)
                    break
            else:
                saga.state = SagaState.COMPLETED
                self._log(saga, "saga.completed")
        except Exception as e:
            saga.state = SagaState.FAILED
            saga.error = str(e)
            self._log(saga, f"saga.failed: {e}")
        finally:
            saga.completed_at = datetime.now(timezone.utc)
            self._active.pop(saga.saga_id, None)

            if self.producer:
                try:
                    await self.producer.publish("saga.events", make_event(
                        f"saga.{saga.state.value.lower()}",
                        {
                            "saga_id": saga.saga_id,
                            "name": saga.name,
                            "state": saga.state.value,
                            "completed_steps": saga.completed_steps,
                            "failed_step": saga.failed_step,
                            "error": saga.error,
                        },
                        producer="faccp-saga-orchestrator",
                    ))
                except Exception:
                    pass

        return saga

    async def _compensate(self, saga: Saga) -> None:
        saga.state = SagaState.COMPENSATING
        self._log(saga, "saga.compensating")

        for step_name in reversed(saga.completed_steps):
            step = next((s for s in saga.steps if s.name == step_name), None)
            if not step or not step.compensation:
                continue

            try:
                self._log(saga, f"compensation.starting: {step.compensation.name}")
                await asyncio.wait_for(
                    step.compensation.func(**step.compensation.args, saga_context=saga.context),
                    timeout=step.timeout_seconds,
                )
                self._log(saga, f"compensation.completed: {step.compensation.name}")
            except Exception as e:
                logger.exception("compensation_failed", saga_id=saga.saga_id, step=step_name)
                saga.error = f"Compensation of {step_name} failed: {e}"
                saga.state = SagaState.FAILED
                self._log(saga, f"compensation.failed: {step_name}: {e}")
                return

        saga.state = SagaState.COMPENSATED
        self._log(saga, "saga.compensated")

    def _log(self, saga: Saga, message: str) -> None:
        entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "message": message}
        saga.history.append(entry)
        logger.info("saga.event", saga_id=saga.saga_id, **entry)

    def get_active(self) -> list[Saga]:
        return list(self._active.values())
