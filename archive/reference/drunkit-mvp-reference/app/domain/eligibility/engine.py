"""
Eligibility Engine.

Answers exactly one question: "Is this person, in this jurisdiction,
right now, permitted to view / add / purchase regulated products?"

Hard rule this module exists to enforce: the API independently
evaluates eligibility on every state-changing call (add to cart,
checkout). A disabled button on the frontend is a UX nicety, never
the security boundary. See evaluate_actions() below and its usage in
the order API.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.eligibility.policy_store import get_policy


class EligibilityDecision(str):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE_AGE = "INELIGIBLE_AGE"
    INELIGIBLE_JURISDICTION = "INELIGIBLE_JURISDICTION"
    INELIGIBLE_MISSING_DOB = "INELIGIBLE_MISSING_DOB"
    INELIGIBLE_UNVERIFIED = "INELIGIBLE_UNVERIFIED"


@dataclass(frozen=True)
class EligibilityResult:
    decision: str
    can_view: bool
    can_add_to_cart: bool
    can_checkout: bool
    reason: str
    minimum_age_required: int | None
    state_key: str


def _calculate_age(date_of_birth: date, as_of: date | None = None) -> int:
    as_of = as_of or date.today()
    years = as_of.year - date_of_birth.year
    had_birthday = (as_of.month, as_of.day) >= (date_of_birth.month, date_of_birth.day)
    return years if had_birthday else years - 1


def evaluate_eligibility(
    *,
    state_key: str | None,
    date_of_birth: datetime | date | None,
) -> EligibilityResult:
    """
    Pure function: no DB, no side effects. Callers are responsible for
    persisting/logging the outcome via the audit log. Kept pure so it's
    trivially unit-testable against every policy permutation.
    """
    if not state_key:
        return EligibilityResult(
            decision=EligibilityDecision.INELIGIBLE_JURISDICTION,
            can_view=True,
            can_add_to_cart=False,
            can_checkout=False,
            reason="No delivery jurisdiction provided.",
            minimum_age_required=None,
            state_key="UNKNOWN",
        )

    policy = get_policy(state_key)

    if not policy.allow_delivery:
        return EligibilityResult(
            decision=EligibilityDecision.INELIGIBLE_JURISDICTION,
            can_view=True,  # browsing can still be shown; transacting cannot
            can_add_to_cart=False,
            can_checkout=False,
            reason=f"Delivery of regulated products is not enabled for {policy.state_key}.",
            minimum_age_required=policy.minimum_age,
            state_key=policy.state_key,
        )

    if date_of_birth is None:
        return EligibilityResult(
            decision=EligibilityDecision.INELIGIBLE_MISSING_DOB,
            can_view=True,
            can_add_to_cart=False,
            can_checkout=False,
            reason="Date of birth has not been verified.",
            minimum_age_required=policy.minimum_age,
            state_key=policy.state_key,
        )

    dob = date_of_birth.date() if isinstance(date_of_birth, datetime) else date_of_birth
    age = _calculate_age(dob)
    min_age = policy.minimum_age or 21  # conservative fallback if policy omits it

    if age < min_age:
        return EligibilityResult(
            decision=EligibilityDecision.INELIGIBLE_AGE,
            can_view=True,
            can_add_to_cart=False,
            can_checkout=False,
            reason=f"Minimum legal age in {policy.state_key} is {min_age}.",
            minimum_age_required=min_age,
            state_key=policy.state_key,
        )

    return EligibilityResult(
        decision=EligibilityDecision.ELIGIBLE,
        can_view=True,
        can_add_to_cart=True,
        can_checkout=True,
        reason="Eligibility verified.",
        minimum_age_required=min_age,
        state_key=policy.state_key,
    )
