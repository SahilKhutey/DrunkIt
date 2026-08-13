"""
Unit tests for Phase 12 Support Agent Service (Schemas, Messages, Tickets, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/support-agent")
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

from app.schemas.support import SupportMessageRequest, SupportTicketCreate
from scripts.constitution.check_support_agent_service import SupportAgentServiceChecker


def test_support_message_request_valid():
    msg = SupportMessageRequest(
        user_id="usr_consumer_101",
        content="How do I register my Karnataka state excise permit?",
    )
    assert msg.user_id == "usr_consumer_101"


def test_support_ticket_create_valid():
    tck = SupportTicketCreate(
        subject="Permit upload issue",
        description="Unable to verify age proof document",
        priority="HIGH",
    )
    assert tck.subject == "Permit upload issue"


def test_support_agent_service_checker():
    checker = SupportAgentServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
