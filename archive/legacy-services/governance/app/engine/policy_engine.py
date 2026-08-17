def get_field(context: dict, path: str):
    value = context
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def evaluate_condition(condition: dict, context: dict) -> bool:
    actual = get_field(context, condition["field"])
    operator = condition["operator"]
    expected = condition.get("value")

    if operator == "equals":
        return actual == expected
    if operator == "not_equals":
        return actual != expected
    if operator == "exists":
        return actual is not None
    if operator == "greater_than":
        return actual > expected if actual is not None and expected is not None else False
    if operator == "less_than":
        return actual < expected if actual is not None and expected is not None else False

    raise ValueError(f"Unsupported operator: {operator}")


def evaluate_rules(rules: list[dict], context: dict) -> list[dict]:
    results = []
    for rule in rules:
        matched = evaluate_condition(rule["condition"], context)
        results.append({
            "rule": rule.get("id", "rule_1"),
            "matched": matched,
            "action": rule.get("action") if matched else None,
        })
    return results


class PolicyEngine:

    def evaluate(self, rules: list[dict], context: dict) -> dict:
        evaluated = evaluate_rules(rules, context)
        all_passed = all(r["matched"] for r in evaluated)
        return {
            "decision": "ALLOW" if all_passed else "DENY",
            "rules_evaluated": evaluated,
        }
