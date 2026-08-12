"""
Unit tests for Phase 8 Realtime Service (ConnectionManager, Schemas, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/realtime-service")
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

from app.schemas.realtime import BroadcastMessageRequest
from app.services.realtime_service import ConnectionManager
from scripts.constitution.check_realtime_service import RealtimeServiceChecker


def test_broadcast_message_request_valid():
    msg = BroadcastMessageRequest(
        topic="order",
        channel_id="ORD-20260812-9A8B",
        event_type="order.updated",
        data={"status": "CONFIRMED"},
    )
    assert msg.topic == "order"


def test_connection_manager_initialization():
    mgr = ConnectionManager()
    channels, conns = mgr.get_stats()
    assert channels == 0
    assert conns == 0


def test_realtime_service_checker():
    checker = RealtimeServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
