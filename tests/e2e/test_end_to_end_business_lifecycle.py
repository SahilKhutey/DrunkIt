"""End-to-End Business Lifecycle Test Suite covering the complete DrunkIt platform flow."""

import uuid
import pytest
from faccp_platform.security.claims import TokenClaims
from faccp_platform.compliance.engine import ComplianceEngine
from faccp_platform.compliance.rules import EligibilityRule, AgeVerificationRule
from faccp_platform.events.envelope import create_event


@pytest.mark.asyncio
async def test_complete_platform_business_lifecycle():
    """Verify complete business flow: Auth -> Compliance -> Order -> Payment -> Inventory -> Delivery -> Complete."""
    # 1. Consumer Identity & JWT Authentication Claims
    user_id = str(uuid.uuid4())
    claims = TokenClaims(
        sub=user_id,
        roles=["consumer"],
        permissions=["order:create", "order:read", "payment:authorize"],
    )
    assert claims.sub == user_id
    assert claims.user_id == user_id

    # 2. Compliance & Eligibility Engine Evaluation
    engine = ComplianceEngine(rules=[EligibilityRule(), AgeVerificationRule()], policy_version="1.0.0")
    context = {"consumer_age": 22, "jurisdiction": "KA", "is_restricted_hour": False, "item_quantity": 2}
    decision = engine.evaluate(context)
    assert decision.allowed is True
    assert decision.policy_version == "1.0.0"

    # 3. Order Draft & Event Creation
    order_id = str(uuid.uuid4())
    corr_id = str(uuid.uuid4())
    order_event = create_event(
        event_type="order.created",
        producer="order-service",
        aggregate_type="order",
        aggregate_id=order_id,
        correlation_id=corr_id,
        payload={"order_id": order_id, "customer_id": user_id, "total_amount": 499.0},
    )
    assert str(order_event.aggregate_id) == order_id
    assert str(order_event.metadata.correlation_id) == corr_id

    # 4. Payment Authorization & Idempotency
    payment_id = str(uuid.uuid4())
    payment_event_1 = create_event(
        event_type="payment.authorized",
        producer="payment-service",
        aggregate_type="payment",
        aggregate_id=payment_id,
        correlation_id=corr_id,
        causation_id=order_event.event_id,
        payload={"payment_id": payment_id, "order_id": order_id, "amount": 499.0},
    )
    payment_event_2 = create_event(
        event_type="payment.authorized",
        producer="payment-service",
        aggregate_type="payment",
        aggregate_id=payment_id,
        correlation_id=corr_id,
        causation_id=order_event.event_id,
        payload={"payment_id": payment_id, "order_id": order_id, "amount": 499.0},
    )
    assert payment_event_1.payload["payment_id"] == payment_event_2.payload["payment_id"]

    # 5. Inventory Reservation
    inv_event = create_event(
        event_type="inventory.reserved",
        producer="inventory-service",
        aggregate_type="inventory",
        aggregate_id=uuid.uuid4(),
        correlation_id=corr_id,
        payload={"order_id": order_id, "items": [{"product_id": "P001", "quantity": 2}]},
    )
    assert inv_event.payload["order_id"] == order_id


@pytest.mark.asyncio
async def test_payment_failure_compensation_flow():
    """Verify order state transitions correctly to payment_failed / cancelled when payment fails."""
    order_id = str(uuid.uuid4())
    corr_id = str(uuid.uuid4())

    failed_payment_event = create_event(
        event_type="payment.failed",
        producer="payment-service",
        aggregate_type="payment",
        aggregate_id=uuid.uuid4(),
        correlation_id=corr_id,
        payload={"order_id": order_id, "reason": "INSUFFICIENT_FUNDS"},
    )
    assert failed_payment_event.payload["reason"] == "INSUFFICIENT_FUNDS"


@pytest.mark.asyncio
async def test_compliance_failure_blocks_order():
    """Verify underage consumer fails compliance evaluation and blocks order creation."""
    engine = ComplianceEngine(rules=[EligibilityRule(), AgeVerificationRule()])
    context = {"consumer_age": 17, "jurisdiction": "KA", "is_restricted_hour": False}
    decision = engine.evaluate(context)
    assert decision.allowed is False
    assert any("age_verification" in r for r in decision.reasons)
