"""Unit of Work pattern managing database transactions, audit logging, and outbox event dispatch."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.audit import AuditLog, OutboxEvent


class SyncUnitOfWork:
    """Synchronous Unit of Work managing atomic transactions and audit/outbox entries."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def __enter__(self) -> "SyncUnitOfWork":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        self.session.rollback()

    def record_audit(
        self,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        correlation_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Record an immutable audit log entry."""
        audit_entry = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            metadata_json=(metadata or {}),
        )
        self.session.add(audit_entry)
        return audit_entry

    def publish_outbox(
        self,
        event_type: str,
        payload: dict[str, Any],
        aggregate_type: str | None = None,
        aggregate_id: uuid.UUID | None = None,
        correlation_id: uuid.UUID | None = None,
        causation_id: uuid.UUID | None = None,
        schema_version: int = 1,
    ) -> OutboxEvent:
        """Write an outbox event to be dispatched asynchronously by background workers."""
        outbox_event = OutboxEvent(
            event_type=event_type,
            schema_version=schema_version,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            payload=payload,
        )
        self.session.add(outbox_event)
        return outbox_event


class AsyncUnitOfWork:
    """Asynchronous Unit of Work managing atomic transactions and audit/outbox entries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> "AsyncUnitOfWork":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        """Commit the current transaction asynchronously."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction asynchronously."""
        await self.session.rollback()

    async def record_audit(
        self,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        correlation_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Record an immutable audit log entry asynchronously."""
        audit_entry = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            metadata_json=(metadata or {}),
        )
        self.session.add(audit_entry)
        return audit_entry

    async def publish_outbox(
        self,
        event_type: str,
        payload: dict[str, Any],
        aggregate_type: str | None = None,
        aggregate_id: uuid.UUID | None = None,
        correlation_id: uuid.UUID | None = None,
        causation_id: uuid.UUID | None = None,
        schema_version: int = 1,
    ) -> OutboxEvent:
        """Write an outbox event asynchronously."""
        outbox_event = OutboxEvent(
            event_type=event_type,
            schema_version=schema_version,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
            payload=payload,
        )
        self.session.add(outbox_event)
        return outbox_event
