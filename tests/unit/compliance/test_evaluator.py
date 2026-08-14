"""Unit tests for compliance rule evaluator and operator comparisons."""

import uuid
from types import SimpleNamespace
from services.compliance.app.domain.enums import Operator, RuleType
from services.compliance.app.engine.evaluator import compare, evaluate_rule, resolve_field


def make_rule(operator, field, value, rule_type=RuleType.AGE, blocking=True):
    return SimpleNamespace(
        id=uuid.uuid4(),
        name="Test Rule",
        rule_type=rule_type,
        operator=operator,
        field=field,
        value={"value": value},
        blocking=blocking,
    )


def test_resolve_field():
    ctx = {"consumer": {"age": 21, "profile": {"name": "Alice"}}}
    assert resolve_field(ctx, "consumer.age") == 21
    assert resolve_field(ctx, "consumer.profile.name") == "Alice"
    assert resolve_field(ctx, "consumer.missing") is None


def test_compare_operator_logic():
    assert compare(Operator.GTE, 21, 21) is True
    assert compare(Operator.GTE, 20, 21) is False
    assert compare(Operator.EQ, True, True) is True
    assert compare(Operator.EQ, False, True) is False
    assert compare(Operator.LTE, 2, 2) is True
    assert compare(Operator.LTE, 3, 2) is False
    assert compare(Operator.GTE, None, 21) is False


def test_evaluate_rule_edge_cases():
    ctx = SimpleNamespace(
        consumer=SimpleNamespace(age=21, verified=True),
        product=SimpleNamespace(quantity=2),
    )

    # 1. Age exactly minimum
    r1 = make_rule(Operator.GTE, "consumer.age", 21)
    res1 = evaluate_rule(r1, ctx)
    assert res1.passed is True

    # 2. Age below minimum
    r2 = make_rule(Operator.GTE, "consumer.age", 25)
    res2 = evaluate_rule(r2, ctx)
    assert res2.passed is False
    assert res2.reason_code == "age_requirement_failed"

    # 3. Verification missing/false
    ctx_unverified = SimpleNamespace(consumer=SimpleNamespace(age=21, verified=False))
    r3 = make_rule(Operator.EQ, "consumer.verified", True, rule_type=RuleType.VERIFICATION)
    res3 = evaluate_rule(r3, ctx_unverified)
    assert res3.passed is False
    assert res3.reason_code == "verification_required"
