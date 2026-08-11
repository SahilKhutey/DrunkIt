"""Compliance policy management routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db
from faccp_common.dto import APIResponse
from faccp_common.exceptions import NotFoundError

from app.api.dependencies import get_policy_service, verify_admin
from app.schemas.policy import (
    DryDayCreate, DryDayResponse, EvaluateRequest, EvaluateResponse,
    JurisdictionCreate, JurisdictionResponse, OverrideRequest, PolicyCreate,
    PolicyResponse,
)
from app.services.policy_service import PolicyService

router = APIRouter(tags=["Compliance Policies"])


@router.post("/jurisdictions", status_code=201)
async def create_jurisdiction(
    payload: JurisdictionCreate,
    service: Annotated[PolicyService, Depends(get_policy_service)],
    _: Annotated[dict, Depends(verify_admin)],
) -> APIResponse[JurisdictionResponse]:
    j = await service.create_jurisdiction(
        code=payload.code, name=payload.name, level=payload.level,
        country_code=payload.country_code, parent_code=payload.parent_code,
        config=payload.config,
    )
    return APIResponse(
        data=JurisdictionResponse(
            id=j.id, code=j.code, name=j.name, level=j.level,
            country_code=j.country_code, is_active=j.is_active,
        )
    )


@router.get("/jurisdictions")
async def list_jurisdictions(
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> APIResponse[list[JurisdictionResponse]]:
    from sqlalchemy import select
    from app.db.models import Jurisdiction
    result = await service.db.execute(select(Jurisdiction).where(Jurisdiction.is_active == True))  # noqa: E712
    items = [
        JurisdictionResponse(
            id=j.id, code=j.code, name=j.name, level=j.level,
            country_code=j.country_code, is_active=j.is_active,
        )
        for j in result.scalars().all()
    ]
    return APIResponse(data=items)


@router.post("/policies", status_code=201)
async def create_policy(
    payload: PolicyCreate,
    service: Annotated[PolicyService, Depends(get_policy_service)],
    _: Annotated[dict, Depends(verify_admin)],
) -> APIResponse[PolicyResponse]:
    p = await service.create_policy(
        jurisdiction_code=payload.jurisdiction_code,
        policy_type=payload.policy_type,
        version=payload.version,
        name=payload.name,
        rules=payload.rules,
        effective_from=payload.effective_from,
        effective_until=payload.effective_until,
        approved_by=payload.approved_by,
        source_document=payload.source_document,
    )
    return APIResponse(data=PolicyResponse(
        id=p.id, jurisdiction_code=payload.jurisdiction_code,
        policy_type=p.policy_type, version=p.version, name=p.name,
        description=p.description, rules=p.rules, effective_from=p.effective_from,
        effective_until=p.effective_until, is_active=p.is_active,
        approved_by=p.approved_by, approved_at=p.approved_at, checksum=p.checksum,
    ))


@router.get("/policies/{jurisdiction_code}/{policy_type}")
async def get_active_policy(
    jurisdiction_code: str,
    policy_type: str,
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> APIResponse[PolicyResponse]:
    p = await service.get_active_policy(jurisdiction_code, policy_type)
    if p is None:
        raise NotFoundError(f"No active {policy_type} policy for {jurisdiction_code}")
    return APIResponse(data=PolicyResponse(
        id=p.id, jurisdiction_code=jurisdiction_code, policy_type=p.policy_type,
        version=p.version, name=p.name, description=p.description, rules=p.rules,
        effective_from=p.effective_from, effective_until=p.effective_until,
        is_active=p.is_active, approved_by=p.approved_by, approved_at=p.approved_at,
        checksum=p.checksum,
    ))


@router.post("/dry-days", status_code=201)
async def add_dry_day(
    payload: DryDayCreate,
    service: Annotated[PolicyService, Depends(get_policy_service)],
    _: Annotated[dict, Depends(verify_admin)],
) -> APIResponse[DryDayResponse]:
    dd = await service.add_dry_day(
        jurisdiction_code=payload.jurisdiction_code, day=payload.date,
        reason=payload.reason, approved_by=payload.approved_by,
        is_recurring=payload.is_recurring, recurring_rule=payload.recurring_rule,
    )
    return APIResponse(data=DryDayResponse(
        id=dd.id, jurisdiction_code=payload.jurisdiction_code, date=dd.date,
        reason=dd.reason, is_recurring=dd.is_recurring, approved_by=dd.approved_by,
    ))


@router.post("/evaluate")
async def evaluate(
    payload: EvaluateRequest,
    service: Annotated[PolicyService, Depends(get_policy_service)],
) -> APIResponse[EvaluateResponse]:
    """Evaluate a subject (typically an order) against all applicable policies."""
    result = await service.evaluate_order(payload)
    return APIResponse(data=result)
