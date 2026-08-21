"""Comprehensive test suite for Deterministic Regulatory & Compliance Engine."""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.compliance import ComplianceCheck, ComplianceDecision
from app.models.audit import OutboxEvent


def test_legal_age_and_verified_consumer_allowed(client: TestClient) -> None:
    """Verify compliant check with verified adult in West Bengal returns ALLOWED."""
    # Set time to a normal business hour (e.g. 2:00 PM on a non-dry day)
    check_time = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc)

    payload = {
        "jurisdiction_code": "IN-WB",
        "consumer_age": 24,
        "is_age_verified": True,
        "product_class": "SPIRITS",
        "channel": "ONLINE_ORDER",
        "total_volume_ml": 750,
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOWED"
    assert data["jurisdiction_code"] == "IN-WB"
    assert "COMPLIANCE_SATISFIED" in data["reason_codes"]
    assert len(data["required_checks"]) == 0


def test_underage_consumer_denied(client: TestClient) -> None:
    """Verify underage consumer in West Bengal (age 19 vs LDA 21) returns DENIED."""
    check_time = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc)

    payload = {
        "jurisdiction_code": "IN-WB",
        "consumer_age": 19,
        "is_age_verified": True,
        "product_class": "SPIRITS",
        "channel": "ONLINE_ORDER",
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "DENIED"
    assert "UNDERAGE_DENIED" in data["reason_codes"]


def test_unverified_age_requires_verification(client: TestClient) -> None:
    """Verify unverified age returns REQUIRES_VERIFICATION."""
    check_time = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc)

    payload = {
        "jurisdiction_code": "IN-WB",
        "consumer_age": None,
        "is_age_verified": False,
        "product_class": "SPIRITS",
        "channel": "ONLINE_ORDER",
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "REQUIRES_VERIFICATION"
    assert "AGE_VERIFICATION_REQUIRED" in data["required_checks"]


def test_delivery_channel_prohibition_in_karnataka(client: TestClient) -> None:
    """Verify delivery channel in Karnataka (IN-KA) returns DENIED with DELIVERY_PROHIBITED."""
    check_time = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc)

    payload = {
        "jurisdiction_code": "IN-KA",
        "consumer_age": 28,
        "is_age_verified": True,
        "product_class": "SPIRITS",
        "channel": "HOME_DELIVERY",
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "DENIED"
    assert "DELIVERY_PROHIBITED_IN_JURISDICTION" in data["reason_codes"]


def test_delivery_channel_allowed_in_west_bengal(client: TestClient) -> None:
    """Verify delivery channel in West Bengal (IN-WB) returns ALLOWED."""
    check_time = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc)

    payload = {
        "jurisdiction_code": "IN-WB",
        "consumer_age": 28,
        "is_age_verified": True,
        "product_class": "SPIRITS",
        "channel": "HOME_DELIVERY",
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOWED"


def test_dry_day_denial_on_gandhi_jayanti(client: TestClient) -> None:
    """Verify checkout check on October 2 (Gandhi Jayanti) returns DENIED for dry day."""
    check_time = datetime(2026, 10, 2, 14, 0, 0, tzinfo=timezone.utc)

    payload = {
        "jurisdiction_code": "IN-WB",
        "consumer_age": 30,
        "is_age_verified": True,
        "channel": "ONLINE_ORDER",
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "DENIED"
    assert "DRY_DAY_DENIED" in data["reason_codes"]


def test_outside_operating_hours_denial(client: TestClient) -> None:
    """Verify order attempt at 3:00 AM returns OUTSIDE_OPERATING_HOURS denial."""
    check_time = datetime(2026, 6, 15, 3, 0, 0, tzinfo=timezone.utc)

    payload = {
        "jurisdiction_code": "IN-WB",
        "consumer_age": 30,
        "is_age_verified": True,
        "channel": "ONLINE_ORDER",
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "DENIED"
    assert "OUTSIDE_OPERATING_HOURS" in data["reason_codes"]


def test_possession_limit_exceeded_denial(client: TestClient) -> None:
    """Verify volume exceeding state possession limits (e.g. 5,000ml in Karnataka vs 2,300ml max) returns DENIED."""
    check_time = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc)

    payload = {
        "jurisdiction_code": "IN-KA",
        "consumer_age": 30,
        "is_age_verified": True,
        "product_class": "SPIRITS",
        "channel": "IN_STORE",
        "total_volume_ml": 5000,
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "DENIED"
    assert "POSSESSION_LIMIT_EXCEEDED" in data["reason_codes"]


def test_compliance_database_persistence_and_outbox(client: TestClient, db_session: Session) -> None:
    """Verify ComplianceCheck, ComplianceDecision, and OutboxEvent records are saved in DB."""
    check_time = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
    correlation_id = uuid.uuid4()

    payload = {
        "correlation_id": str(correlation_id),
        "jurisdiction_code": "IN-WB",
        "consumer_age": 28,
        "is_age_verified": True,
        "current_time": check_time.isoformat(),
    }
    response = client.post("/api/v1/compliance/check", json=payload)
    assert response.status_code == 200

    # Query DB
    check_record = db_session.scalars(
        select(ComplianceCheck).where(ComplianceCheck.correlation_id == correlation_id)
    ).first()
    assert check_record is not None
    assert check_record.decision is not None
    assert check_record.decision.decision == "ALLOWED"

    # Query Outbox
    outbox = db_session.scalars(
        select(OutboxEvent).where(
            OutboxEvent.event_type == "COMPLIANCE_EVALUATED",
            OutboxEvent.correlation_id == correlation_id,
        )
    ).first()
    assert outbox is not None
    assert outbox.payload["decision"] == "ALLOWED"


def test_jurisdiction_policy_summary_endpoints(client: TestClient) -> None:
    """Verify GET /api/v1/compliance/jurisdictions and GET /api/v1/compliance/jurisdictions/{code}."""
    # 1. List all summaries
    res_list = client.get("/api/v1/compliance/jurisdictions")
    assert res_list.status_code == 200
    summaries = res_list.json()
    assert len(summaries) >= 4

    # 2. Get specific jurisdiction (West Bengal)
    res_wb = client.get("/api/v1/compliance/jurisdictions/IN-WB")
    assert res_wb.status_code == 200
    wb_data = res_wb.json()
    assert wb_data["jurisdiction_code"] == "IN-WB"
    assert wb_data["legal_drinking_age"]["spirits"] == 21
    assert wb_data["channels"]["home_delivery"]["allowed"] is True
