import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/risk-service")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/recommendation-service")))

import pytest
from faccp_common.federation import JurisdictionRouter, FederatedRequest, TenantContext
from faccp_common.saga import SagaOrchestrator, Saga, SagaStep, CompensationAction
from faccp_common.privacy import detect_pii, redact_pii, k_anonymize, anonymize_for_analytics
from faccp_common.slo import ErrorBudget
from app.ml.feature_engineering import FeatureExtractor
from app.ml.fraud_detector import FraudDetectionEnsemble, get_fraud_ensemble
from app.services.recommender import ProductRecommender



def test_ml_risk_feature_extractor_and_ensemble():
    context = {
        "account_age_days": 10,
        "failed_verifications": 1,
        "total_orders": 2,
        "trust_score": 75,
        "vpn_detected": True,
        "geo_distance_from_home_km": 120,
    }
    history = [{"amount": 1500, "minutes_ago": 15}]
    ensemble = get_fraud_ensemble()
    result = ensemble.evaluate(context, history, rule_score=0.2, user_id="usr-123")

    assert "final_score" in result
    assert "ml_probability" in result
    assert "is_anomaly" in result
    assert isinstance(result["top_contributors"], list)


def test_federation_jurisdiction_router():
    router = JurisdictionRouter()
    req = FederatedRequest(
        request_id="req-1",
        jurisdiction_code="IN-KA",
        consumer_id="cons-1",
        payload={"consumer_region": "IN-S"},
    )
    decision = router.route(req)
    assert decision["action"] == "route"
    assert decision["jurisdiction"] == "IN-KA"
    assert decision["region"] == "IN-S"


@pytest.mark.asyncio
async def test_saga_orchestrator_success():
    orchestrator = SagaOrchestrator()
    executed_steps = []

    async def step1(ctx):
        executed_steps.append("step1")
        return "ok1"

    async def step2(ctx):
        executed_steps.append("step2")
        return "ok2"

    saga = Saga(
        name="test_saga",
        steps=[
            SagaStep(name="step1", action=step1),
            SagaStep(name="step2", action=step2),
        ],
    )
    res = await orchestrator.execute(saga)
    assert res.state.value == "COMPLETED"
    assert executed_steps == ["step1", "step2"]


@pytest.mark.asyncio
async def test_saga_orchestrator_compensation():
    orchestrator = SagaOrchestrator()
    compensated = []

    async def step1(ctx):
        return "ok1"

    async def comp1(**kwargs):
        compensated.append("comp1")

    async def step2_fail(ctx):
        raise ValueError("Simulated step2 failure")

    saga = Saga(
        name="failing_saga",
        steps=[
            SagaStep(name="step1", action=step1, compensation=CompensationAction(name="comp1", func=comp1)),
            SagaStep(name="step2", action=step2_fail),
        ],
    )
    res = await orchestrator.execute(saga)
    assert res.state.value == "COMPENSATED"
    assert compensated == ["comp1"]


def test_privacy_engineering():
    text = "User contact is john.doe@example.com and phone +919876543210"
    pii = detect_pii(text)
    assert "email" in pii
    assert "phone_in" in pii

    redacted = redact_pii(text)
    assert "john.doe@example.com" not in redacted
    assert "[REDACTED]" in redacted

    kanon = k_anonymize(["A", "A", "A", "A", "A", "B"], k=5)
    assert kanon[0] == "A"
    assert kanon[-1].startswith("bucket_")

    anon = anonymize_for_analytics({"email": "a@b.com", "user_id": "u1", "amount": 150})
    assert "email" not in anon
    assert anon["amount"] == 150


def test_ai_recommender():
    rec = ProductRecommender()
    rec.set_product_attributes("p100", {"name": "Whisky", "category": "spirit", "brand": "B1"})
    rec.set_product_attributes("p200", {"name": "IPA", "category": "beer", "brand": "B2"})
    rec.record_interaction("u1", "p100", "purchase")
    rec.record_interaction("u2", "p100", "purchase")
    rec.record_interaction("u2", "p200", "purchase")

    recommendations = rec.recommend("u1", n=5)
    assert len(recommendations) > 0
    assert recommendations[0]["product_id"] == "p200"
