from uuid import uuid4


class PolicyMock:

    def __init__(self, policy_code: str, jurisdiction_id: str, version: str, status: str, rules: dict | list):
        self.id = str(uuid4())
        self.policy_code = policy_code
        self.jurisdiction_id = jurisdiction_id
        self.version = version
        self.status = status
        self.rules = rules


class PolicyService:

    def __init__(self):
        self.policies: dict[str, PolicyMock] = {}
        # Pre-seed a default active policy
        default_p = PolicyMock(
            policy_code="ALCOHOL_HOME_DELIVERY",
            jurisdiction_id="IN-STATE-X",
            version="2026.01",
            status="ACTIVE",
            rules={
                "rule_list": [
                    {
                        "id": "consumer_verification",
                        "type": "REQUIREMENT",
                        "condition": {
                            "field": "consumer_verification_status",
                            "operator": "equals",
                            "value": "VERIFIED",
                        },
                        "failure": "DENY",
                        "message": "Consumer identity/age not verified",
                    }
                ]
            },
        )
        self.policies[f"IN-STATE-X:CREATE_ALCOHOL_ORDER"] = default_p

    async def get_policy(self, jurisdiction_id: str, operation: str) -> PolicyMock | None:
        key = f"{jurisdiction_id}:{operation}"
        if key in self.policies:
            return self.policies[key]
        # Return fallback active policy if jurisdiction exists
        return self.policies.get("IN-STATE-X:CREATE_ALCOHOL_ORDER")

    async def activate_policy(self, policy: PolicyMock) -> PolicyMock:
        policy.status = "ACTIVE"
        key = f"{policy.jurisdiction_id}:{policy.policy_code}"
        self.policies[key] = policy
        return policy
