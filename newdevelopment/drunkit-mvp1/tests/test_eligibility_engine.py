from datetime import date

from app.domain.eligibility.engine import EligibilityDecision, evaluate_eligibility
from app.domain.eligibility.policy_store import clear_cache


def test_unknown_state_fails_closed():
    result = evaluate_eligibility(state_key="NOWHERELAND", date_of_birth=date(1990, 1, 1))
    assert result.decision == EligibilityDecision.INELIGIBLE_JURISDICTION
    assert result.can_checkout is False
    assert result.can_add_to_cart is False


def test_no_state_provided_blocks_transaction():
    result = evaluate_eligibility(state_key=None, date_of_birth=date(1990, 1, 1))
    assert result.decision == EligibilityDecision.INELIGIBLE_JURISDICTION
    assert result.can_view is True
    assert result.can_checkout is False


def test_missing_dob_blocks_but_allows_browsing():
    # EXAMPLE_STATE_DO_NOT_USE in the shipped policy file has
    # allow_delivery=false, so this exercises the jurisdiction path.
    # We don't assert on a real allowed state here since the shipped
    # policy file intentionally contains no legally-reviewed states.
    result = evaluate_eligibility(state_key="EXAMPLE_STATE_DO_NOT_USE", date_of_birth=None)
    assert result.can_view is True
    assert result.can_checkout is False


def test_underage_blocked_when_state_allows_delivery(monkeypatch, tmp_path):
    # Build an isolated policy file with a permissive test jurisdiction
    # so this test doesn't depend on mutating the shared policy file.
    import json

    policy_file = tmp_path / "jurisdictions.json"
    policy_file.write_text(
        json.dumps(
            {
                "default": {"allow_delivery": False, "minimum_age": None},
                "states": {
                    "TESTLAND": {"allow_delivery": True, "minimum_age": 21},
                },
            }
        )
    )

    import app.domain.eligibility.policy_store as policy_store

    monkeypatch.setattr(policy_store, "POLICY_FILE", policy_file)
    clear_cache()

    underage = evaluate_eligibility(state_key="TESTLAND", date_of_birth=date.today().replace(year=date.today().year - 18))
    assert underage.decision == EligibilityDecision.INELIGIBLE_AGE
    assert underage.can_checkout is False

    adult = evaluate_eligibility(state_key="TESTLAND", date_of_birth=date(1990, 1, 1))
    assert adult.decision == EligibilityDecision.ELIGIBLE
    assert adult.can_checkout is True

    clear_cache()  # restore for other tests


def test_age_calculation_handles_birthday_not_yet_occurred():
    from app.domain.eligibility.engine import _calculate_age

    # Born Dec 31, "today" is Jan 1 of the following year minus a day
    # before the birthday occurs that year.
    dob = date(2000, 12, 31)
    as_of = date(2020, 12, 30)  # one day before 20th birthday
    assert _calculate_age(dob, as_of=as_of) == 19

    as_of_after = date(2020, 12, 31)  # birthday itself
    assert _calculate_age(dob, as_of=as_of_after) == 20
