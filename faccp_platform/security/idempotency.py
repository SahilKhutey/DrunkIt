"""Security idempotency key validation and replay protection."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from fastapi import HTTPException
from sqlalchemy import JSON, String, select
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base


class IdempotencyRecord(Base):
    """Idempotency record tracking request payload hash and cached responses."""

    __tablename__ = "idempotency_records"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    request_hash: Mapped[str] = mapped_column(String(64))
    response_status: Mapped[int] = mapped_column()
    response_body: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


def calculate_payload_hash(payload: Any) -> str:
    """Calculate SHA-256 hash of canonical JSON request payload."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_idempotency_key(
    existing_record: IdempotencyRecord | None,
    incoming_hash: str,
) -> dict[str, Any] | None:
    """Validate incoming request hash against existing record. Raise 409 if reused with different payload."""
    if existing_record is None:
        return None
    if existing_record.request_hash != incoming_hash:
        raise HTTPException(
            status_code=409,
            detail="Idempotency key reused with different request payload",
        )
    return existing_record.response_body
