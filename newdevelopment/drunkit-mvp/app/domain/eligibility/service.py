from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.db import models
from app.domain.eligibility.engine import EligibilityDecision, EligibilityResult, evaluate_eligibility


def verify_consumer_eligibility(
    db: Session,
    *,
    consumer: models.Consumer,
    state_key: str,
    date_of_birth: date | None,
) -> EligibilityResult:
    """
    Runs the eligibility engine, persists the consumer's verified state
    (never the raw DOB verification document — that belongs in a
    dedicated identity/verification service, not here), and writes an
    append-only audit log entry regardless of outcome.
    """
    dob_to_check = date_of_birth or (
        consumer.date_of_birth.date() if consumer.date_of_birth else None
    )

    result = evaluate_eligibility(state_key=state_key, date_of_birth=dob_to_check)

    if date_of_birth is not None:
        consumer.date_of_birth = datetime.combine(date_of_birth, datetime.min.time())
    consumer.state = state_key.strip().upper().replace(" ", "_")
    consumer.eligibility_state = (
        models.EligibilityState.VERIFIED
        if result.decision == EligibilityDecision.ELIGIBLE
        else models.EligibilityState.FAILED
    )
    if result.decision == EligibilityDecision.ELIGIBLE:
        consumer.eligibility_verified_at = utcnow()

    log = models.EligibilityCheckLog(
        consumer_id=consumer.id,
        state=result.state_key,
        minimum_age_required=result.minimum_age_required,
        outcome=consumer.eligibility_state,
        reason=result.reason,
    )
    db.add(log)
    db.add(consumer)
    db.commit()
    db.refresh(consumer)

    return result


def get_current_eligibility(db: Session, *, consumer: models.Consumer) -> EligibilityResult:
    """
    Re-derives the live eligibility decision from stored state, rather
    than trusting a cached boolean. Called on every add-to-cart and
    checkout request server-side — this is the actual enforcement
    point, independent of anything the frontend claims.
    """
    dob = consumer.date_of_birth.date() if consumer.date_of_birth else None
    return evaluate_eligibility(state_key=consumer.state, date_of_birth=dob)
