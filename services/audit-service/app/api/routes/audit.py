"""Audit service API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db
from faccp_common.dto import APIResponse, PaginatedResponse, paginated
from faccp_common.exceptions import UnauthorizedError
from faccp_common.security import decode_token

from app.api.dependencies import get_audit_service
from app.config import get_settings
from app.schemas.audit import (
    AuditEventCreate, AuditEventResponse, AuditSearchRequest,
    ChainVerificationResult,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])
settings = get_settings()


@router.post("/events", status_code=201)
async def create_event(
    payload: AuditEventCreate,
    service: Annotated[AuditService, Depends(get_audit_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[AuditEventResponse]:
    """Append a new audit event. Requires a valid service or admin token."""
    if not authorization:
        raise UnauthorizedError("Authentication required")
    try:
        token = authorization.replace("Bearer ", "").strip()
        decode_token(
            token, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            expected_type="access",
        )
    except Exception as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e

    event = await service.append(**payload.model_dump(exclude_none=True))
    return APIResponse(data=AuditEventResponse(
        id=event.id, event_id=event.event_id, sequence_number=event.sequence_number,
        actor_id=event.actor_id, actor_type=event.actor_type, actor_role=event.actor_role,
        actor_ip=event.actor_ip, action=event.action, resource_type=event.resource_type,
        resource_id=event.resource_id, event_type=event.event_type, result=event.result,
        severity=event.severity, service_name=event.service_name,
        correlation_id=event.correlation_id, payload=event.payload,
        occurred_at=event.occurred_at, received_at=event.received_at,
        previous_hash=event.previous_hash, event_hash=event.event_hash,
    ))


@router.post("/search")
async def search_events(
    payload: AuditSearchRequest,
    service: Annotated[AuditService, Depends(get_audit_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[PaginatedResponse[AuditEventResponse]]:
    """Search audit events. Requires auditor/admin role."""
    if not authorization:
        raise UnauthorizedError("Authentication required")
    try:
        token = authorization.replace("Bearer ", "").strip()
        claims = decode_token(
            token, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            expected_type="access",
        )
    except Exception as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e
    if not any(r in claims.get("roles", []) for r in ["SUPER_ADMIN", "AUDITOR", "INTERNAL_AUDITOR", "SECURITY_ADMIN"]):
        raise UnauthorizedError("Auditor role required")

    events, total = await service.search(**payload.model_dump(exclude_none=True))
    items = [
        AuditEventResponse(
            id=e.id, event_id=e.event_id, sequence_number=e.sequence_number,
            actor_id=e.actor_id, actor_type=e.actor_type, actor_role=e.actor_role,
            actor_ip=e.actor_ip, action=e.action, resource_type=e.resource_type,
            resource_id=e.resource_id, event_type=e.event_type, result=e.result,
            severity=e.severity, service_name=e.service_name,
            correlation_id=e.correlation_id, payload=e.payload,
            occurred_at=e.occurred_at, received_at=e.received_at,
            previous_hash=e.previous_hash, event_hash=e.event_hash,
        )
        for e in events
    ]
    return APIResponse(data=paginated(items, payload.page, payload.page_size, total))


@router.get("/verify")
async def verify_chain(
    service: Annotated[AuditService, Depends(get_audit_service)],
    from_sequence: int = Query(default=1, ge=1),
    to_sequence: int | None = Query(default=None, ge=1),
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[ChainVerificationResult]:
    """Verify the integrity of the audit chain. Requires auditor role."""
    if not authorization:
        raise UnauthorizedError("Authentication required")
    try:
        token = authorization.replace("Bearer ", "").strip()
        claims = decode_token(
            token, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            expected_type="access",
        )
    except Exception as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e
    if not any(r in claims.get("roles", []) for r in ["SUPER_ADMIN", "AUDITOR", "INTERNAL_AUDITOR"]):
        raise UnauthorizedError("Auditor role required")
    result = await service.verify_chain(from_sequence, to_sequence)
    return APIResponse(data=ChainVerificationResult(**result))
