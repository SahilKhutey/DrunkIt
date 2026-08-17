from datetime import datetime, timezone
from uuid import uuid4
from services.governance.app.engine.policy_engine import PolicyEngine
from services.governance.app.models.policy import PolicyStatus

VALID_TRANSITIONS = {
    PolicyStatus.DRAFT.value: {PolicyStatus.REVIEW.value},
    PolicyStatus.REVIEW.value: {PolicyStatus.DRAFT.value, PolicyStatus.APPROVED.value},
    PolicyStatus.APPROVED.value: {PolicyStatus.SCHEDULED.value, PolicyStatus.ACTIVE.value},
    PolicyStatus.SCHEDULED.value: {PolicyStatus.ACTIVE.value},
    PolicyStatus.ACTIVE.value: {PolicyStatus.RETIRED.value},
}


class PolicyService:

    def __init__(self, policy_engine: PolicyEngine | None = None):
        self.policy_engine = policy_engine or PolicyEngine()
        self.policies: dict[str, dict] = {}

    async def create_policy(self, name: str, jurisdiction: str, scope: str, rules: list[dict], effective_from: datetime | None = None) -> dict:
        pol_id = f"POL-{uuid4().hex[:8]}"
        rec = {
            "id": str(uuid4()),
            "policy_id": pol_id,
            "name": name,
            "version": 1,
            "status": PolicyStatus.DRAFT.value,
            "jurisdiction": jurisdiction,
            "scope": scope,
            "rules": rules,
            "effective_from": effective_from or datetime.now(timezone.utc),
        }
        self.policies[pol_id] = rec
        return rec

    async def transition_status(self, policy_id: str, target_status: str) -> dict:
        pol = self.policies.get(policy_id)
        if not pol:
            raise ValueError("POLICY_NOT_FOUND")

        current = pol["status"]
        allowed = VALID_TRANSITIONS.get(current, set())
        if target_status not in allowed:
            raise ValueError(f"Invalid transition {current} -> {target_status}")

        pol["status"] = target_status
        return pol

    async def evaluate_policy(self, policy_id: str, context: dict) -> dict:
        pol = self.policies.get(policy_id)
        if not pol:
            raise ValueError("POLICY_NOT_FOUND")
        return self.policy_engine.evaluate(pol["rules"], context)
