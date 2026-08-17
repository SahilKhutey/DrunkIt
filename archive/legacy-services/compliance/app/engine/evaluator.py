"""Safe rule evaluator for eligibility contexts."""

from __future__ import annotations

from typing import Any
from ..domain.decision import RuleResult
from ..domain.enums import DecisionReasonCode, Operator, RuleType


def resolve_field(obj: Any, path: str) -> Any:
    """Resolve dot-separated property path on objects or dictionaries."""
    parts = path.split(".")
    current = obj
    for part in parts:
        if current is None:
            return None
        if hasattr(current, part):
            current = getattr(current, part)
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def compare(operator: str | Operator, actual: Any, expected: Any) -> bool:
    """Safely compare actual vs expected value with null & type guard."""
    if actual is None:
        return False
    op_val = operator.value if isinstance(operator, Operator) else str(operator)
    try:
        if op_val == Operator.EQ.value:
            return actual == expected
        if op_val == Operator.NE.value:
            return actual != expected
        if op_val == Operator.GT.value:
            return actual > expected
        if op_val == Operator.GTE.value:
            return actual >= expected
        if op_val == Operator.LT.value:
            return actual < expected
        if op_val == Operator.LTE.value:
            return actual <= expected
        if op_val == Operator.IN.value:
            return actual in expected
        if op_val == Operator.NOT_IN.value:
            return actual not in expected
    except TypeError:
        return False
    return False


def get_reason_code_for_rule(rule_type: str | RuleType | None) -> DecisionReasonCode:
    """Map failed rule type to standardized DecisionReasonCode."""
    rt = rule_type.value if isinstance(rule_type, RuleType) else str(rule_type or "")
    if rt == RuleType.AGE.value:
        return DecisionReasonCode.AGE_REQUIREMENT_FAILED
    if rt == RuleType.VERIFICATION.value:
        return DecisionReasonCode.VERIFICATION_REQUIRED
    if rt == RuleType.QUANTITY.value:
        return DecisionReasonCode.QUANTITY_LIMIT_EXCEEDED
    if rt == RuleType.PRODUCT.value:
        return DecisionReasonCode.PRODUCT_RESTRICTED
    if rt == RuleType.TIME.value:
        return DecisionReasonCode.TIME_RESTRICTION
    if rt == RuleType.LOCATION.value:
        return DecisionReasonCode.LOCATION_RESTRICTED
    return DecisionReasonCode.PRODUCT_RESTRICTED


def evaluate_rule(rule: Any, context: Any) -> RuleResult:
    """Evaluate a single ComplianceRule against EligibilityContext."""
    actual = resolve_field(context, rule.field)
    val_dict = rule.value if isinstance(rule.value, dict) else {}
    expected = val_dict.get("value") if isinstance(rule.value, dict) else rule.value

    passed = compare(rule.operator, actual, expected)
    r_code = None if passed else get_reason_code_for_rule(getattr(rule, "rule_type", None))

    return RuleResult(
        rule_id=rule.id,
        passed=passed,
        reason=f"{rule.name}: {'passed' if passed else 'failed'}",
        blocking=getattr(rule, "blocking", True),
        reason_code=r_code,
    )
