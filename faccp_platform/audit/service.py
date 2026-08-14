"""Tamper-evident audit hashing, hash chain verification, and AuditService."""

from __future__ import annotations

import hashlib
import json
from typing import Any
from .models import AuditLog


class AuditService:
    """Audit service helper for logging security and business events."""

    def __init__(self, session: Any = None) -> None:
        self.session = session

    async def record(
        self,
        action: str,
        actor_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Record audit log entry for historical compatibility."""
        return await self.log_event(
            event_type=action,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            outcome="success",
            payload=metadata or {},
        )

    async def log_event(
        self,
        event_type: str,
        actor_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        action: str = "execute",
        outcome: str = "success",
        payload: dict[str, Any] | None = None,
        actor_type: str = "user",
        service: str = "faccp-service",
    ) -> AuditLog:
        rec = {
            "event_type": event_type,
            "actor_id": actor_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "outcome": outcome,
            "payload": payload or {},
        }
        prev_hash = "0" * 64
        rec_hash = hash_record(prev_hash, rec)

        log_entry = AuditLog(
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            service=service,
            resource_type=resource_type or "system",
            resource_id=resource_id,
            action=action,
            outcome=outcome,
            payload=payload or {},
            previous_hash=prev_hash,
            record_hash=rec_hash,
        )
        if self.session:
            self.session.add(log_entry)
            await self.session.flush()
        return log_entry


def hash_record(previous_hash: str, record: dict[str, Any]) -> str:
    """Calculate SHA-256 hash of previous_hash and record dictionary."""
    canonical = json.dumps(
        {
            "previous_hash": previous_hash,
            "record": record,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_chain(records: list[dict[str, Any]]) -> bool:
    """Verify tamper-evident integrity of an ordered audit record chain."""
    if not records:
        return True

    expected_prev = "0" * 64
    for record in records:
        recorded_prev = record.get("previous_hash", "0" * 64)
        recorded_hash = record.get("record_hash")
        data = record.get("data", {})

        if recorded_prev != expected_prev:
            return False

        computed = hash_record(recorded_prev, data)
        if computed != recorded_hash:
            return False

        expected_prev = recorded_hash

    return True
