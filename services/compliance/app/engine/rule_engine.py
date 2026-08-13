from typing import Any

OPERATORS = {
    "equals",
    "not_equals",
    "in",
    "not_in",
    "greater_than",
    "less_than",
    "greater_equal",
    "less_equal",
    "exists",
}


class RuleEngine:

    def evaluate_condition(self, actual: Any, operator: str, expected: Any) -> bool:
        if operator not in OPERATORS:
            raise ValueError(f"UNSUPPORTED_OPERATOR: {operator}")

        if operator == "equals":
            return actual == expected

        if operator == "not_equals":
            return actual != expected

        if operator == "in":
            return actual in expected if expected is not None else False

        if operator == "not_in":
            return actual not in expected if expected is not None else True

        if operator == "greater_than":
            return actual > expected

        if operator == "less_than":
            return actual < expected

        if operator == "greater_equal":
            return actual >= expected

        if operator == "less_equal":
            return actual <= expected

        if operator == "exists":
            return actual is not None

        return False

    def evaluate_rule(self, rule: dict, context: Any) -> dict:
        rule_id = rule.get("id", "unknown_rule")
        condition = rule.get("condition", {})
        field_path = condition.get("field", "")
        operator = condition.get("operator", "equals")
        expected = condition.get("value")

        # Resolve field from context
        actual = getattr(context, field_path, None) if hasattr(context, field_path) else None

        passed = self.evaluate_condition(actual, operator, expected)
        return {
            "rule": rule_id,
            "passed": passed,
            "failure_action": rule.get("failure", "DENY") if not passed else None,
            "message": rule.get("message", f"Rule {rule_id} evaluation failed") if not passed else "OK",
        }

    def evaluate(self, context: Any, rules: list[dict]) -> list[dict]:
        results = []
        for rule in rules:
            results.append(self.evaluate_rule(rule, context))
        return results
