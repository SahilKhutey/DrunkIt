import os
import sys
import json
from datetime import date

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
drunkit_mvp_path = os.path.join(root_dir, "services", "drunkit-mvp")

def _setup_mvp_env():
    sys.path = [p for p in sys.path if not ("services" in p and p != drunkit_mvp_path)]
    if drunkit_mvp_path not in sys.path:
        sys.path.insert(0, drunkit_mvp_path)
    for mod_name in list(sys.modules.keys()):
        if mod_name == "app" or mod_name.startswith("app."):
            del sys.modules[mod_name]

_setup_mvp_env()

from app.domain.eligibility.engine import EligibilityDecision, evaluate_eligibility, _calculate_age
from app.domain.eligibility import policy_store
from app.domain.eligibility.policy_store import clear_cache


def test_unknown_state_fails_closed():
    _setup_mvp_env()
    result = evaluate_eligibility(state_key="NOWHERELAND", date_of_birth=date(1990, 1, 1))
    assert result.decision == EligibilityDecision.INELIGIBLE_JURISDICTION
    assert result.can_checkout is False
    assert result.can_add_to_cart is False


def test_no_state_provided_blocks_transaction():
    _setup_mvp_env()
    result = evaluate_eligibility(state_key=None, date_of_birth=date(1990, 1, 1))
    assert result.decision == EligibilityDecision.INELIGIBLE_JURISDICTION
    assert result.can_view is True
    assert result.can_checkout is False


def test_missing_dob_blocks_but_allows_browsing():
    _setup_mvp_env()
    result = evaluate_eligibility(state_key="EXAMPLE_STATE_DO_NOT_USE", date_of_birth=None)
    assert result.can_view is True
    assert result.can_checkout is False


def test_underage_blocked_when_state_allows_delivery(monkeypatch, tmp_path):
    _setup_mvp_env()
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

    monkeypatch.setattr(policy_store, "POLICY_FILE", policy_file)
    clear_cache()

    underage = evaluate_eligibility(state_key="TESTLAND", date_of_birth=date.today().replace(year=date.today().year - 18))
    assert underage.decision == EligibilityDecision.INELIGIBLE_AGE
    assert underage.can_checkout is False

    adult = evaluate_eligibility(state_key="TESTLAND", date_of_birth=date(1990, 1, 1))
    assert adult.decision == EligibilityDecision.ELIGIBLE
    assert adult.can_checkout is True

    clear_cache()


def test_age_calculation_handles_birthday_not_yet_occurred():
    _setup_mvp_env()
    dob = date(2000, 12, 31)
    as_of = date(2020, 12, 30)
    assert _calculate_age(dob, as_of=as_of) == 19

    as_of_after = date(2020, 12, 31)
    assert _calculate_age(dob, as_of=as_of_after) == 20
