"""Compliance audit retrieval service."""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.decision import EligibilityDecisionModel
from ..repositories.decision import DecisionRepository


class AuditService:
    """Service retrieving and recording compliance decision audit records."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session
        self.repository = DecisionRepository(session) if session is not None else None

    async def get_decision(self, decision_id: str | uuid.UUID) -> EligibilityDecisionModel | None:
        """Fetch decision audit log by decision_id."""
        if self.repository is None:
            return None
        return await self.repository.get(decision_id)

    async def record(self, action_type: str, resource_id: str, metadata: Any = None) -> dict[str, Any]:
        """Legacy helper for tamper-evident audit recording."""
        payload_str = json.dumps(metadata or {}, default=str)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        return {
            "id": str(uuid.uuid4()),
            "action_type": action_type,
            "resource_id": resource_id,
            "payload_hash": payload_hash,
            "metadata": metadata,
        }
