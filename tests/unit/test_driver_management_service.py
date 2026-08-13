"""
Unit tests for Master Phase D2 Driver Management System auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_driver_management_service import (
    DriverManagementServiceChecker,
    DRIVER_MANAGEMENT_MAP,
)


def test_driver_management_service_auditor_report():
    checker = DriverManagementServiceChecker(root_dir=root_dir)
    res = checker.audit_driver_management_service()

    assert res["total_modules"] == 10
    assert res["verified_modules"] == 10
    assert res["score_pct"] == 100.0
    assert len(DRIVER_MANAGEMENT_MAP) == 10

    # Test key modules across Enums, State Machine, Models, Repositories, Services, APIs
    assert DRIVER_MANAGEMENT_MAP["DRV-D2-01"] == "DriverAccountStatus Enum (PENDING, ACTIVE, SUSPENDED, DEACTIVATED)"
    assert DRIVER_MANAGEMENT_MAP["DRV-D2-02"] == "DriverOperationalStatus Enum (OFFLINE, AVAILABLE, RESERVED, ASSIGNED, PICKING_UP, DELIVERING, PAUSED)"
    assert DRIVER_MANAGEMENT_MAP["DRV-D2-04"] == "Operational State Machine Validation Engine"
    assert DRIVER_MANAGEMENT_MAP["DRV-D2-07"] == "Driver Service Layer (create_driver, change_status enforcing active & verified checks)"
    assert DRIVER_MANAGEMENT_MAP["DRV-D2-08"] == "Location Telemetry Service & API Endpoint (/drivers/{id}/location)"
    assert DRIVER_MANAGEMENT_MAP["DRV-D2-09"] == "Internal Availability Discovery Endpoint (/internal/drivers/available)"
    assert DRIVER_MANAGEMENT_MAP["DRV-D2-10"] == "Admin Approval Boundary Protection (Self-activation prohibited for PENDING drivers)"
