import pytest
from faccp_common.replication import GCounter, PNCounter, ORSet, LWWRegister, MVRegister, VectorClock, RegionManager, Region
from faccp_common.dsl import WorkflowParser, WorkflowEngine, WorkflowContext, WorkflowEvent, evaluate_condition
from faccp_common.integrations import StubKYCAdapter, StubPaymentAdapter, StubSMSAdapter, StubEmailAdapter, IntegrationRegistry


def test_replication_crdts():
    gc1 = GCounter(node_id="node1")
    gc2 = GCounter(node_id="node2")
    gc1.increment(5)
    gc2.increment(3)
    gc1.merge(gc2)
    assert gc1.value() == 8

    pn1 = PNCounter(node_id="node1")
    pn2 = PNCounter(node_id="node2")
    pn1.increment(10)
    pn1.decrement(2)
    pn2.decrement(3)
    pn1.merge(pn2)
    assert pn1.value() == 5

    orset1 = ORSet(node_id="node1")
    orset2 = ORSet(node_id="node2")
    orset1.add("itemA")
    orset2.add("itemB")
    orset1.merge(orset2)
    assert "itemA" in orset1.value()
    assert "itemB" in orset1.value()

    lww1 = LWWRegister(initial="v1", node_id="node1")
    lww2 = LWWRegister(initial="v2", node_id="node2")
    lww1.merge(lww2)
    assert lww1.value() in ("v1", "v2")


def test_vector_clocks():
    vc1 = VectorClock(node_id="A")
    vc2 = VectorClock(node_id="B")
    vc1.tick()
    vc2.tick()
    assert vc1.concurrent_with(vc2)

    vc1.observe(vc2)
    assert vc1.dominates(vc2)


def test_state_machine_dsl_parser_and_evaluator():
    yaml_content = """
name: test_wf
version: "1.0"
variables:
  score: 90
states:
  - name: START
    is_initial: true
  - name: APPROVED
    is_final: true
transitions:
  - from_state: START
    to_state: APPROVED
    event: pass
    condition: score >= 80
"""
    wf = WorkflowParser.parse(yaml_content, format="yaml")
    assert wf.name == "test_wf"
    assert len(wf.states) == 2
    assert len(wf.transitions) == 1

    assert evaluate_condition("score >= 80", {"score": 90}) is True
    assert evaluate_condition("score < 50", {"score": 90}) is False


@pytest.mark.asyncio
async def test_workflow_engine_execution():
    yaml_content = """
name: execution_wf
version: "1.0"
states:
  - name: INIT
    is_initial: true
  - name: COMPLETED
    is_final: true
transitions:
  - from_state: INIT
    to_state: COMPLETED
    event: finish
"""
    wf = WorkflowParser.parse(yaml_content, format="yaml")
    engine = WorkflowEngine(workflow=wf)
    ctx = WorkflowContext()
    await engine.start(ctx)
    assert ctx.current_state == "INIT"

    await engine.send_event(ctx, WorkflowEvent(event_type="finish"))
    assert ctx.current_state == "COMPLETED"
    assert ctx.state.value == "COMPLETED"


@pytest.mark.asyncio
async def test_integration_adapters():
    kyc = StubKYCAdapter()
    assert await kyc.health_check() is True
    check = await kyc.create_check("usr-1", {"first_name": "John"})
    assert "check_id" in check

    age_res = await kyc.verify_age("usr-1", {"date_of_birth": "2000-01-01"})
    assert age_res["age_eligible"] is True

    payment = StubPaymentAdapter()
    assert await payment.health_check() is True
    intent = await payment.create_intent(1500, "INR", {"order_id": "ord-1"})
    assert intent["status"] == "requires_payment_method"

    sms = StubSMSAdapter()
    assert await sms.health_check() is True
    res_sms = await sms.send("+919876543210", "Your OTP is 123456")
    assert res_sms["status"] == "sent"

    email = StubEmailAdapter()
    assert await email.health_check() is True
    res_email = await email.send("test@example.com", "Subject", "<p>Body</p>")
    assert res_email["status"] == "sent"

    registry = IntegrationRegistry()
    registry.register("kyc", kyc)
    registry.register("payment", payment)
    assert len(registry.list()) == 2
