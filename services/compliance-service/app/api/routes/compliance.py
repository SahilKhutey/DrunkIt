"""Compliance API routes."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_compliance_service
from app.schemas.compliance import (
    ComplianceEvaluationRequest, ComplianceEvaluationResult, DryDayCreate,
    DryDayResponse, PolicyCreate, PolicyResponse,
)
from app.services.compliance_service import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Compliance Engine"])


@router.post("/policies", response_model=SuccessResponse[PolicyResponse], status_code=201)
async def create_policy(
    payload: PolicyCreate,
    service: Annotated[ComplianceService, Depends(get_compliance_service)],
) -> SuccessResponse[PolicyResponse]:
    policy = await service.create_policy(payload)
    return SuccessResponse(data=PolicyResponse(
        id=policy.id, code=policy.code, title=policy.title, description=policy.description,
        jurisdiction=policy.jurisdiction, category=policy.category, is_active=policy.is_active,
        effective_from=policy.effective_from, effective_until=policy.effective_until,
        min_purchasing_age=policy.min_purchasing_age,
        max_volume_per_transaction_ml=policy.max_volume_per_transaction_ml,
        max_volume_per_day_ml=policy.max_volume_per_day_ml,
        sales_start_time=policy.sales_start_time, sales_end_time=policy.sales_end_time,
        created_at=policy.created_at,
    ), message="Policy created successfully")


@router.get("/policies", response_model=SuccessResponse[list[PolicyResponse]])
async def list_policies(
    jurisdiction: str | None = Query(default=None),
    service: Annotated[ComplianceService, Depends(get_compliance_service)] = None,
) -> SuccessResponse[list[PolicyResponse]]:
    policies = await service.list_policies(jurisdiction)
    return SuccessResponse(data=[PolicyResponse(
        id=p.id, code=p.code, title=p.title, description=p.description,
        jurisdiction=p.jurisdiction, category=p.category, is_active=p.is_active,
        effective_from=p.effective_from, effective_until=p.effective_until,
        min_purchasing_age=p.min_purchasing_age,
        max_volume_per_transaction_ml=p.max_volume_per_transaction_ml,
        max_volume_per_day_ml=p.max_volume_per_day_ml,
        sales_start_time=p.sales_start_time, sales_end_time=p.sales_end_time,
        created_at=p.created_at,
    ) for p in policies])


@router.get("/policies/{code}", response_model=SuccessResponse[PolicyResponse])
async def get_policy(
    code: str,
    service: Annotated[ComplianceService, Depends(get_compliance_service)],
) -> SuccessResponse[PolicyResponse]:
    p = await service.get_policy(code)
    return SuccessResponse(data=PolicyResponse(
        id=p.id, code=p.code, title=p.title, description=p.description,
        jurisdiction=p.jurisdiction, category=p.category, is_active=p.is_active,
        effective_from=p.effective_from, effective_until=p.effective_until,
        min_purchasing_age=p.min_purchasing_age,
        max_volume_per_transaction_ml=p.max_volume_per_transaction_ml,
        max_volume_per_day_ml=p.max_volume_per_day_ml,
        sales_start_time=p.sales_start_time, sales_end_time=p.sales_end_time,
        created_at=p.created_at,
    ))


@router.post("/dry-days", response_model=SuccessResponse[DryDayResponse], status_code=201)
async def add_dry_day(
    payload: DryDayCreate,
    service: Annotated[ComplianceService, Depends(get_compliance_service)],
) -> SuccessResponse[DryDayResponse]:
    dry = await service.add_dry_day(payload)
    return SuccessResponse(data=DryDayResponse(
        id=dry.id, jurisdiction=dry.jurisdiction, dry_date=dry.dry_date,
        occasion=dry.occasion, is_full_day=dry.is_full_day,
    ), message="Dry day recorded")


@router.get("/dry-days/check")
async def check_dry_day(
    jurisdiction: str,
    check_date: date = Query(default_factory=date.today),
    service: Annotated[ComplianceService, Depends(get_compliance_service)] = None,
) -> SuccessResponse[dict]:
    is_dry, occasion = await service.is_dry_day(jurisdiction, check_date)
    return SuccessResponse(data={
        "jurisdiction": jurisdiction,
        "check_date": check_date.isoformat(),
        "is_dry_day": is_dry,
        "occasion": occasion,
    })


@router.post("/evaluate", response_model=SuccessResponse[ComplianceEvaluationResult])
async def evaluate_transaction(
    payload: ComplianceEvaluationRequest,
    service: Annotated[ComplianceService, Depends(get_compliance_service)],
) -> SuccessResponse[ComplianceEvaluationResult]:
    result = await service.evaluate_transaction(payload)
    return SuccessResponse(data=result, message="Evaluation complete")
