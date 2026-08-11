"""Dependencies for the compliance service."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db
from faccp_common.exceptions import UnauthorizedError
from faccp_common.kafka_client import EventProducer
from faccp_common.security import decode_token

from app.config import get_settings
from app.services.policy_service import PolicyService

settings = get_settings()


async def get_event_producer(request: Request) -> EventProducer | None:
    return getattr(request.app.state, "event_producer", None)


def get_policy_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    producer: Annotated[EventProducer | None, Depends(get_event_producer)] = None,
) -> PolicyService:
    return PolicyService(db=db, producer=producer)


async def verify_admin(
    authorization: Annotated[str | None, Header()] = None,
) -> dict:
    """Require admin-level role from internal service token."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Admin authentication required")
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = decode_token(
            token,
            secret=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            expected_type="access",
        )
    except Exception as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e
    roles = claims.get("roles", [])
    if not any(r in roles for r in ["SUPER_ADMIN", "REGULATORY_ADMIN", "STATE_ADMIN", "COMPLIANCE_OFFICER"]):
        raise UnauthorizedError("Admin role required")
    return claims
