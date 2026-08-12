"""Audit API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_audit_service
from app.schemas.audit import (
    AuditEntryCreate, AuditEntryResponse, ChainVerificationResponse,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Cryptographic Audit Ledger"])


@router.post("/logs", response_model=SuccessResponse[AuditEntryResponse], status_code=201)
async def log_event(
    payload: AuditEntryCreate,
    service: Annotated[AuditService, Depends(get_audit_service)],
) -> SuccessResponse[AuditEntryResponse]:
    entry = await service.log_event(payload)
    return SuccessResponse(data=AuditEntryResponse(
        id=entry.id, sequence_number=entry.sequence_number, event_id=entry.event_id,
        event_type=entry.event_type, actor_id=entry.actor_id, actor_role=entry.actor_role,
        resource_type=entry.resource_type, resource_id=entry.resource_id,
        previous_hash=entry.previous_hash, current_hash=entry.current_hash,
        recorded_at=entry.recorded_at,
    ), message="Event logged to cryptographic audit chain")


@router.get("/logs", response_model=SuccessResponse[list[AuditEntryResponse]])
async def list_logs(
    service: Annotated[AuditService, Depends(get_audit_service)],
    limit: int = 50,
) -> SuccessResponse[list[AuditEntryResponse]]:
    entries = await service.list_logs(limit=limit)
    return SuccessResponse(data=[AuditEntryResponse(
        id=e.id, sequence_number=e.sequence_number, event_id=e.event_id,
        event_type=e.event_type, actor_id=e.actor_id, actor_role=e.actor_role,
        resource_type=e.resource_type, resource_id=e.resource_id,
        previous_hash=e.previous_hash, current_hash=e.current_hash,
        recorded_at=e.recorded_at,
    ) for e in entries])


@router.get("/verify-chain", response_model=SuccessResponse[ChainVerificationResponse])
async def verify_chain(
    service: Annotated[AuditService, Depends(get_audit_service)],
) -> SuccessResponse[ChainVerificationResponse]:
    res = await service.verify_chain()
    return SuccessResponse(data=res, message="Audit chain verification complete")
