from services.compliance.app.engine.rule_engine import RuleEngine


class DecisionEngine:

    def __init__(self, policy_service=None, rule_engine=None):
        self.policy_service = policy_service
        self.rule_engine = rule_engine or RuleEngine()

    async def decide(self, context) -> dict:
        policy = None
        if self.policy_service:
            policy = await self.policy_service.get_policy(context.jurisdiction_id, context.operation)

        if not policy:
            return {
                "decision": "DENY",
                "reasons": [{"rule": "POLICY_CHECK", "message": "NO_ACTIVE_POLICY"}],
                "policy_version": "NONE",
            }

        rules = policy.rules if isinstance(policy.rules, list) else policy.rules.get("rule_list", [])
        results = self.rule_engine.evaluate(context, rules)

        failures = [r for r in results if not r["passed"]]

        if failures:
            requires_review = any(r.get("failure_action") == "REVIEW" for r in failures)
            decision_type = "REVIEW" if requires_review else "DENY"
            return {
                "decision": decision_type,
                "reasons": failures,
                "policy_version": getattr(policy, "version", "1.0.0"),
            }

        return {
            "decision": "ALLOW",
            "reasons": [],
            "policy_version": getattr(policy, "version", "1.0.0"),
        }
