"""
Loads jurisdiction policy from policies/jurisdictions.json.

This is intentionally the ONLY place that reads that file. Every other
module asks this module a yes/no question — nothing else is allowed to
parse jurisdiction rules independently, or you'll end up with drift
between "what the policy file says" and "what the code actually checks."
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

POLICY_FILE = Path(__file__).resolve().parents[3] / "policies" / "jurisdictions.json"


@dataclass(frozen=True)
class JurisdictionPolicy:
    state_key: str
    allow_delivery: bool
    minimum_age: int | None
    legal_basis_ref: str | None
    notes: str | None


class PolicyNotFoundError(Exception):
    pass


@lru_cache
def _load_raw() -> dict:
    if not POLICY_FILE.exists():
        raise PolicyNotFoundError(f"Jurisdiction policy file missing at {POLICY_FILE}")
    return json.loads(POLICY_FILE.read_text())


def get_policy(state_key: str) -> JurisdictionPolicy:
    """
    Returns the policy for a state. Never raises for an unknown state —
    it returns the 'default' entry, which must be allow_delivery=false.
    This is the fail-closed behavior: an unreviewed or misspelled state
    key results in a refusal, not an accidental approval.
    """
    raw = _load_raw()
    state_key_norm = state_key.strip().upper().replace(" ", "_")
    entry = raw.get("states", {}).get(state_key_norm) or raw["default"]

    return JurisdictionPolicy(
        state_key=state_key_norm,
        allow_delivery=bool(entry.get("allow_delivery", False)),
        minimum_age=entry.get("minimum_age"),
        legal_basis_ref=entry.get("legal_basis_ref"),
        notes=entry.get("notes"),
    )


def clear_cache() -> None:
    """Call after editing the policy file in a running process (e.g. tests)."""
    _load_raw.cache_clear()
