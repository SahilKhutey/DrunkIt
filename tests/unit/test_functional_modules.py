"""
Unit tests for Master 66 Functional Architecture Modules auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_functional_modules import FunctionalModulesChecker, FUNCTIONAL_MODULES_MAP


def test_functional_modules_auditor_report():
    checker = FunctionalModulesChecker(root_dir=root_dir)
    res = checker.audit_functional_modules()

    assert res["total_modules"] == 69
    assert res["verified_modules"] == 69
    assert res["score_pct"] == 100.0
    assert len(FUNCTIONAL_MODULES_MAP) == 69


    # Test key modules across all 13 business domains
    assert FUNCTIONAL_MODULES_MAP["ADM-01"] == "Organization Management"
    assert FUNCTIONAL_MODULES_MAP["CON-06"] == "Checkout Pipeline"
    assert FUNCTIONAL_MODULES_MAP["RET-04"] == "Retailer License Management"
    assert FUNCTIONAL_MODULES_MAP["TRU-05"] == "Risk Engine"
    assert FUNCTIONAL_MODULES_MAP["CMP-01"] == "Policy Engine"
    assert FUNCTIONAL_MODULES_MAP["COM-04"] == "Order Engine State Machine"
    assert FUNCTIONAL_MODULES_MAP["FIN-02"] == "Double-Entry Ledger"
    assert FUNCTIONAL_MODULES_MAP["FUL-03"] == "Delivery Lifecycle"
    assert FUNCTIONAL_MODULES_MAP["NTF-01"] == "Notification Engine"
    assert FUNCTIONAL_MODULES_MAP["AUD-01"] == "Audit Event Engine"
    assert FUNCTIONAL_MODULES_MAP["ANL-01"] == "Operational Analytics"
    assert FUNCTIONAL_MODULES_MAP["SUP-01"] == "Customer Support"
    assert FUNCTIONAL_MODULES_MAP["PLT-01"] == "API Gateway"
