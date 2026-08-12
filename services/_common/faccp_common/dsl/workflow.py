"""
State machine DSL — declarative workflow definition and execution.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable

from faccp_common.events import make_event
from faccp_common.exceptions import StateTransitionError, ValidationError
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger

logger = get_logger(__name__)


class WorkflowState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    COMPENSATED = "COMPENSATED"


@dataclass
class Transition:
    from_state: str
    to_state: str
    event: str | None = None
    condition: str | None = None
    action: str | None = None
    timeout_seconds: float | None = None
    requires_role: str | None = None


@dataclass
class State:
    name: str
    is_initial: bool = False
    is_final: bool = False
    on_enter: str | None = None
    on_exit: str | None = None
    timeout_seconds: float | None = None
    timeout_to: str | None = None


@dataclass
class Workflow:
    name: str
    version: str = "1.0"
    description: str = ""
    states: list[State] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)
    actions: dict[str, str] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)

    def get_state(self, name: str) -> State | None:
        return next((s for s in self.states if s.name == name), None)

    def get_initial_state(self) -> State | None:
        return next((s for s in self.states if s.is_initial), None)

    def get_transitions_from(self, state_name: str) -> list[Transition]:
        return [t for t in self.transitions if t.from_state == state_name]

    def validate(self) -> None:
        if not self.states:
            raise ValidationError("Workflow must have at least one state")
        initials = [s for s in self.states if s.is_initial]
        if len(initials) != 1:
            raise ValidationError("Workflow must have exactly one initial state")
        finals = [s for s in self.states if s.is_final]
        if not finals:
            raise ValidationError("Workflow must have at least one final state")
        state_names = {s.name for s in self.states}
        for t in self.transitions:
            if t.from_state not in state_names:
                raise ValidationError(f"Transition from unknown state: {t.from_state}")
            if t.to_state not in state_names:
                raise ValidationError(f"Transition to unknown state: {t.to_state}")


@dataclass
class WorkflowEvent:
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    actor_id: str | None = None
    actor_role: str | None = None


@dataclass
class WorkflowContext:
    instance_id: str = field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:16]}")
    workflow_name: str = ""
    workflow_version: str = "1.0"
    current_state: str = ""
    state: WorkflowState = WorkflowState.PENDING
    variables: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    error: str | None = None
    pending_events: list[WorkflowEvent] = field(default_factory=list)
    wait_reason: str | None = None


class WorkflowEngine:

    def __init__(
        self,
        workflow: Workflow,
        action_executor: Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]] | None = None,
        producer: EventProducer | None = None,
    ) -> None:
        self.workflow = workflow
        self.workflow.validate()
        self._action_executor = action_executor or self._default_action_executor
        self.producer = producer

    async def start(self, context: WorkflowContext, initial_variables: dict[str, Any] | None = None) -> WorkflowContext:
        context.workflow_name = self.workflow.name
        context.workflow_version = self.workflow.version
        context.variables = {**self.workflow.variables, **(initial_variables or {})}
        initial = self.workflow.get_initial_state()
        if not initial:
            raise ValidationError("No initial state")
        context.current_state = initial.name
        context.state = WorkflowState.RUNNING
        self._log(context, f"workflow.started: {initial.name}")
        if initial.on_enter:
            await self._execute_action(context, initial.on_enter)
        await self._process_auto_transitions(context)
        await self._emit(context, "workflow.started")
        return context

    async def send_event(self, context: WorkflowContext, event: WorkflowEvent) -> WorkflowContext:
        if context.state not in (WorkflowState.RUNNING, WorkflowState.WAITING):
            raise StateTransitionError(f"Workflow in state {context.state}, cannot accept events")
        self._log(context, f"event.received: {event.event_type}")
        context.pending_events.append(event)
        return await self._process_events(context)

    async def cancel(self, context: WorkflowContext, reason: str) -> WorkflowContext:
        context.state = WorkflowState.CANCELLED
        context.error = reason
        context.completed_at = datetime.now(timezone.utc)
        self._log(context, f"workflow.cancelled: {reason}")
        await self._emit(context, "workflow.cancelled")
        return context

    async def _process_events(self, context: WorkflowContext) -> WorkflowContext:
        while context.pending_events:
            event = context.pending_events.pop(0)
            transitions = self.workflow.get_transitions_from(context.current_state)
            matched = None
            for t in transitions:
                if t.event and t.event == event.event_type:
                    if t.condition and not self._evaluate_condition(t.condition, context, event):
                        continue
                    if t.requires_role and t.requires_role != event.actor_role:
                        continue
                    matched = t
                    break
            if matched is None:
                self._log(context, f"event.unhandled: {event.event_type}")
                continue
            await self._execute_transition(context, matched, event)
            if context.state in (WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED):
                return context
            await self._process_auto_transitions(context)
        return context

    async def _process_auto_transitions(self, context: WorkflowContext) -> None:
        while True:
            transitions = self.workflow.get_transitions_from(context.current_state)
            auto = [t for t in transitions if t.event is None]
            if not auto:
                break
            matched = None
            for t in auto:
                if t.condition and not self._evaluate_condition(t.condition, context, None):
                    continue
                matched = t
                break
            if matched is None:
                break
            await self._execute_transition(context, matched, None)

    async def _execute_transition(self, context: WorkflowContext, transition: Transition, event: WorkflowEvent | None) -> None:
        from_state = context.current_state
        self._log(context, f"transition: {from_state} -> {transition.to_state} via {transition.event or 'auto'}")
        from_state_obj = self.workflow.get_state(from_state)
        if from_state_obj and from_state_obj.on_exit:
            await self._execute_action(context, from_state_obj.on_exit)
        context.current_state = transition.to_state
        context.variables["_last_transition"] = {
            "from": from_state, "to": transition.to_state,
            "event": transition.event, "at": datetime.now(timezone.utc).isoformat(),
        }
        if event:
            context.variables["_last_event"] = event.payload
        to_state_obj = self.workflow.get_state(transition.to_state)
        if to_state_obj:
            if to_state_obj.is_final:
                context.state = WorkflowState.COMPLETED
                context.completed_at = datetime.now(timezone.utc)
            if to_state_obj.on_enter:
                await self._execute_action(context, to_state_obj.on_enter)
            if to_state_obj.timeout_seconds and to_state_obj.timeout_to and not to_state_obj.is_final:
                asyncio.create_task(self._schedule_timeout(context, to_state_obj))
        if transition.action:
            await self._execute_action(context, transition.action)
        context.updated_at = datetime.now(timezone.utc)
        await self._emit(context, f"workflow.transitioned:{transition.to_state}")

    async def _execute_action(self, context: WorkflowContext, action_name: str) -> None:
        if action_name not in self.workflow.actions:
            self._log(context, f"action.unknown: {action_name}")
            return
        action_expr = self.workflow.actions[action_name]
        try:
            result = await self._action_executor(action_expr, context.variables)
            if result:
                context.variables.update(result)
        except Exception as e:
            self._log(context, f"action.failed: {action_name}: {e}")
            context.state = WorkflowState.FAILED
            context.error = f"Action {action_name} failed: {e}"
            context.completed_at = datetime.now(timezone.utc)
            raise

    def _evaluate_condition(self, condition: str, context: WorkflowContext, event: WorkflowEvent | None) -> bool:
        from faccp_common.dsl.evaluator import evaluate_condition
        return evaluate_condition(condition, context.variables, event.payload if event else None)

    async def _schedule_timeout(self, context: WorkflowContext, state: State) -> None:
        await asyncio.sleep(state.timeout_seconds or 60)
        if context.current_state == state.name and context.state == WorkflowState.RUNNING:
            self._log(context, f"timeout.fired: {state.name}")
            await self._execute_transition(
                context,
                Transition(from_state=state.name, to_state=state.timeout_to or ""),
                None,
            )

    async def _default_action_executor(self, action_expr: str, variables: dict[str, Any]) -> dict[str, Any]:
        logger.info("workflow.action.noop", action=action_expr)
        return {}

    def _log(self, context: WorkflowContext, message: str) -> None:
        entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "message": message}
        context.history.append(entry)
        logger.info("workflow.event", instance=context.instance_id, **entry)

    async def _emit(self, context: WorkflowContext, event_type: str) -> None:
        if self.producer is None: return
        try:
            event = make_event(
                event_type=event_type,
                payload={
                    "instance_id": context.instance_id,
                    "workflow_name": context.workflow_name,
                    "workflow_version": context.workflow_version,
                    "current_state": context.current_state,
                    "state": context.state.value,
                },
                producer="faccp-workflow-engine",
            )
            await self.producer.publish(topic="workflow.events", payload=event)
        except Exception:
            logger.exception("workflow_event_emit_failed")
