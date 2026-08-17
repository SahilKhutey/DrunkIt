from typing import Any
from services.compliance.app.policies.base import CompliancePolicy


class PolicyRegistry:

    def __init__(self):
        self._policies: dict[str, CompliancePolicy] = {}

    def register(
        self,
        jurisdiction: str,
        policy: CompliancePolicy,
    ):
        self._policies[jurisdiction] = policy

    def get(
        self,
        jurisdiction: str,
    ) -> CompliancePolicy:

        policy = self._policies.get(jurisdiction)

        if policy is None:
            raise ValueError(
                f"No policy configured for {jurisdiction}"
            )

        return policy
