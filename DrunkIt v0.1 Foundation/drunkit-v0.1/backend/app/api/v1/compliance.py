"""Compliance API endpoints for regulatory policy evaluation and jurisdictional rule inspection."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.db.session import get_sync_db
from app.db.uow import SyncUnitOfWork
from app.schemas.compliance import (
    ComplianceCheckRequest,
    ComplianceDecisionResponse,
    JurisdictionPolicySummary,
)
from app.services.compliance_service import ComplianceService, PolicyRegistry

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.post(
    "/check",
    response_model=ComplianceDecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate deterministic regulatory compliance",
)
def evaluate_compliance(
    request: ComplianceCheckRequest,
    session: Session = Depends(get_sync_db),
) -> ComplianceDecisionResponse:
    """Evaluate full deterministic compliance ruleset (LDA, dry day, operating hours, channels, possession limits)."""
    uow = SyncUnitOfWork(session)
    with uow:
        decision = ComplianceService.evaluate_compliance(request, uow)
    return decision


@router.get(
    "/jurisdictions",
    response_model=list[JurisdictionPolicySummary],
    status_code=status.HTTP_200_OK,
    summary="List active jurisdictional alcohol regulations",
)
def list_jurisdiction_policies() -> list[JurisdictionPolicySummary]:
    """Retrieve summaries of active state excise policies (LDA, permitted channels, dry days)."""
    return PolicyRegistry.list_summaries()


@router.get(
    "/jurisdictions/{code}",
    response_model=JurisdictionPolicySummary,
    status_code=status.HTTP_200_OK,
    summary="Get regulatory policy for a specific jurisdiction",
)
def get_jurisdiction_policy(code: str) -> JurisdictionPolicySummary:
    """Retrieve detailed regulatory parameters for a specific Indian state (e.g. 'IN-WB' or 'WB')."""
    policy = PolicyRegistry.load_policy(code)
    return JurisdictionPolicySummary(
        jurisdiction_code=policy["jurisdiction_code"],
        jurisdiction_name=policy.get("jurisdiction_name", code),
        version=policy.get("version", "1.0"),
        legal_drinking_age=policy.get("legal_drinking_age", {}),
        channels=policy.get("channels", {}),
        operating_hours=policy.get("operating_hours", {}),
        possession_limits_ml=policy.get("possession_limits_ml", {}),
        dry_days_count=len(policy.get("dry_days_recurring", [])),
    )
