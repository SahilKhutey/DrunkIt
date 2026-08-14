"""Eligibility evaluation API route."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.database.session import get_db_session
from ...schemas.eligibility import EligibilityRequest, EligibilityResponse, RuleResultResponse
from ...services.eligibility_service import EligibilityService

router = APIRouter(prefix="/eligibility", tags=["eligibility"])


@router.post(
    "/evaluate",
    response_model=EligibilityResponse,
)
async def evaluate_eligibility(
    request: EligibilityRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Evaluate compliance eligibility for given context and jurisdiction."""
    service = EligibilityService(session)
    decision = await service.evaluate(
        context=request.context,
        jurisdiction_id=request.jurisdiction_id,
    )
    await session.commit()

    results_resp = [
        RuleResultResponse(
            rule_id=r.rule_id,
            passed=r.passed,
            reason=r.reason,
            blocking=r.blocking,
            reason_code=r.reason_code.value if r.reason_code else None,
        )
        for r in decision.results
    ]

    reason_codes_str = [rc.value if hasattr(rc, "value") else str(rc) for rc in decision.reason_codes]

    return EligibilityResponse(
        decision_id=decision.decision_id,
        status=decision.status.value if hasattr(decision.status, "value") else str(decision.status),
        policy_id=decision.policy_id,
        jurisdiction_id=decision.jurisdiction_id,
        results=results_resp,
        reasons=decision.reasons,
        reason_codes=reason_codes_str,
        engine_version=decision.engine_version,
    )
