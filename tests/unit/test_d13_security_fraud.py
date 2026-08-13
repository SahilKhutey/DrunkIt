"""
Master unit test for Phase D13 Fraud, Abuse & Security Operations Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.security.app.engine.abuse_engine import AccountTakeoverDetector
from services.security.app.engine.decision_engine import OrderSecurityGate
from services.security.app.engine.risk_engine import RiskEngine
from services.security.app.events.consumers import SecurityEventConsumer
from services.security.app.services.action_service import ActionService
from services.security.app.services.case_service import CaseService
from services.security.app.services.device_service import DeviceService
from services.security.app.services.risk_service import RiskService
from services.security.app.services.session_service import SessionService


@pytest.mark.asyncio
async def test_full_d13_security_fraud_pipeline():
    risk_svc = RiskService()

    # 1. Device Intelligence & Multi-Account Signal
    dev_svc = DeviceService()
    dev_res = await dev_svc.link_user("dev-surat-master", "user-surat-1")
    assert dev_res["device"]["status"] == "ACTIVE"

    # 2. Add Risk Signals
    await risk_svc.add_signal("CONSUMER", "user-surat-1", "NEW_DEVICE", 15.0)
    await risk_svc.add_signal("CONSUMER", "user-surat-1", "PASSWORD_RESET", 20.0)
    await risk_svc.add_signal("CONSUMER", "user-surat-1", "PAYMENT_FAILURE", 30.0)

    # 3. Risk Evaluation
    eval_res = await risk_svc.evaluate("CONSUMER", "user-surat-1")
    assert eval_res["risk_score"] == 65.0
    assert eval_res["risk_level"] == "HIGH"
    assert eval_res["decision"] == "HOLD"

    # 4. Account Takeover Detector
    ato_detector = AccountTakeoverDetector()
    ato_score = ato_detector.calculate([{"signal_type": "NEW_DEVICE"}, {"signal_type": "PASSWORD_RESET"}])
    assert ato_score == 35.0

    # 5. Combined Order Security Gate
    gate = OrderSecurityGate()
    comp_allow = {"decision": "ALLOW"}
    sec_hold = {"decision": "HOLD"}
    gate_res = await gate.evaluate(comp_allow, sec_hold)
    assert gate_res["decision"] == "HOLD"
    assert gate_res["reason"] == "SECURITY_REVIEW"

    # 6. Security Case Management & Action Execution
    case_svc = CaseService()
    sec_case = await case_svc.create_case("CONSUMER", "user-surat-1", "ACCOUNT_TAKEOVER", "HIGH")
    assert sec_case["status"] == "OPEN"

    act_svc = ActionService()
    action = await act_svc.execute_action("ORDER_HOLD", "CONSUMER", "user-surat-1", "HIGH_RISK_HOLD")
    assert action["action"] == "ORDER_HOLD"

    # 7. Idempotent Event Consumer
    consumer = SecurityEventConsumer(risk_service=risk_svc)
    event_payload = {"event_id": "evt-dup-100", "type": "payment.failed", "consumer_id": "user-surat-1"}
    handled_first = await consumer.handle_event(event_payload)
    handled_second = await consumer.handle_event(event_payload)

    assert handled_first is True
    assert handled_second is False  # Idempotently rejected second call
