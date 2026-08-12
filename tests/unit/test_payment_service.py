"""
Unit tests for Phase 7 Payment Service (Schemas, Validation, Ledger, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/payment-service")
common_path = os.path.join(root_dir, "services/_common")

for mod_name in list(sys.modules.keys()):
    if mod_name == "app" or mod_name.startswith("app."):
        del sys.modules[mod_name]

if service_path not in sys.path:
    sys.path.insert(0, service_path)
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.schemas.payment import PaymentIntentCreate, PaymentCaptureRequest, PaymentRefundRequest
from scripts.constitution.check_payment_service import PaymentServiceChecker


def test_payment_intent_create_valid():
    intent = PaymentIntentCreate(
        order_id="ORD_SEED_001",
        consumer_id="usr_consumer_101",
        amount_inr=2850.0,
        gateway_provider="STUB_PAY",
    )
    assert intent.order_id == "ORD_SEED_001"
    assert intent.amount_inr == 2850.0


def test_payment_capture_request_valid():
    cap = PaymentCaptureRequest(
        gateway_transaction_id="TXN_STUB_1001",
    )
    assert cap.gateway_transaction_id == "TXN_STUB_1001"


def test_payment_service_checker():
    checker = PaymentServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
