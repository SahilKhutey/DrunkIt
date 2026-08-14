"""Unit tests for deterministic ComplianceEngine decisions."""

import uuid
from types import SimpleNamespace
from services.compliance.app.domain.enums import DecisionStatus, Operator, RuleType
from services.compliance.app.engine.engine import ComplianceEngine


def make_rule(operator, field, value, priority=10, blocking=True, rule_type=RuleType.AGE):
    return SimpleNamespace(
        id=uuid.uuid4(),
        name="Rule",
        rule_type=rule_type,
        operator=operator,
        field=field,
        value={"value": value},
        priority=priority,
        blocking=blocking,
        active=True,
    )


def test_engine_allow():
    engine = ComplianceEngine()
    jurisdiction_id = uuid.uuid4()
    policy = SimpleNamespace(id=uuid.uuid4())
    rules = [
        make_rule(Operator.GTE, "consumer.age", 21, priority=10),
        make_rule(Operator.EQ, "consumer.verified", True, priority=20),
    ]
    context = SimpleNamespace(consumer=SimpleNamespace(age=25, verified=True))

    decision = engine.evaluate(context, policy, rules, jurisdiction_id)
    assert decision.status == DecisionStatus.ALLOW
    assert len(decision.reasons) == 0


def test_engine_deny_blocking_failure():
    engine = ComplianceEngine()
    jurisdiction_id = uuid.uuid4()
    policy = SimpleNamespace(id=uuid.uuid4())
    rules = [
        make_rule(Operator.GTE, "consumer.age", 21, priority=10, blocking=True),
    ]
    context = SimpleNamespace(consumer=SimpleNamespace(age=19, verified=True))

    decision = engine.evaluate(context, policy, rules, jurisdiction_id)
    assert decision.status == DecisionStatus.DENY
    assert "age_requirement_failed" in decision.reason_codes


def test_engine_fail_closed_no_policy():
    engine = ComplianceEngine()
    jurisdiction_id = uuid.uuid4()

    decision = engine.evaluate(context={}, policy=None, rules=[], jurisdiction_id=jurisdiction_id)
    assert decision.status == DecisionStatus.DENY
    assert "no_policy" in decision.reason_codes
