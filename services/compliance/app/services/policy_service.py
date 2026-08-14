"""Policy management service."""

from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.policy import CompliancePolicy
from ..repositories.policy import PolicyRepository
from ..schemas.policy import PolicyCreate


class PolicyService:
    """Service managing compliance policies."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session
        self.repository = PolicyRepository(session) if session is not None else None

    async def get(self, policy_id: str | uuid.UUID) -> CompliancePolicy | None:
        """Fetch policy by ID."""
        if self.repository is None:
            return None
        return await self.repository.get(policy_id)

    async def get_policy(self, jurisdiction_id: str, operation: str = "") -> Any:
        """Legacy helper returning active policy for jurisdiction."""
        if self.repository is None:
            from types import SimpleNamespace
            return SimpleNamespace(
                version="1.0.0",
                rules=[
                    {
                        "field": "consumer_verification_status",
                        "operator": "==",
                        "value": "VERIFIED",
                        "failure_action": "DENY",
                    }
                ],
            )
        return await self.repository.get(jurisdiction_id)

    async def create(self, request: PolicyCreate) -> CompliancePolicy:
        """Create new compliance policy."""
        return await self.repository.create(
            jurisdiction_id=request.jurisdiction_id,
            name=request.name,
            version=request.version,
            effective_from=request.effective_from,
            effective_until=request.effective_until,
            status=request.status,
        )
