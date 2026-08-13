"""
Unit tests for Master Communication System Architecture auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_communication_architecture import (
    CommunicationArchitectureChecker,
    COMMUNICATION_PROTOCOLS_MAP,
)


def test_communication_architecture_auditor_report():
    checker = CommunicationArchitectureChecker(root_dir=root_dir)
    res = checker.audit_communication_architecture()

    assert res["total_protocols"] == 22
    assert res["verified_protocols"] == 22
    assert res["score_pct"] == 100.0
    assert len(COMMUNICATION_PROTOCOLS_MAP) == 22

    # Test key protocols across all 5 layers and controls
    assert COMMUNICATION_PROTOCOLS_MAP["COM-L1-01"] == "Client Communication - HTTPS / REST"
    assert COMMUNICATION_PROTOCOLS_MAP["COM-L2-01"] == "Synchronous Service Communication - Immediate Decision Pipeline"
    assert COMMUNICATION_PROTOCOLS_MAP["COM-L3-01"] == "Asynchronous Event-Driven Bus - Apache Kafka"
    assert COMMUNICATION_PROTOCOLS_MAP["COM-L4-01"] == "Real-Time Broadcast Gateway - WebSocket Session Management"
    assert COMMUNICATION_PROTOCOLS_MAP["COM-L5-01"] == "External Provider Integration Layer & Adapter Interfaces"
    assert COMMUNICATION_PROTOCOLS_MAP["COM-ENV-01"] == "Standard Request Envelope (request_id, correlation_id, actor, payload)"
    assert COMMUNICATION_PROTOCOLS_MAP["COM-REL-02"] == "Reliability Stack - Circuit Breaker Pattern & Recovery Check"
    assert COMMUNICATION_PROTOCOLS_MAP["COM-SEC-01"] == "Communication Security - mTLS & Service Identity Verification"
