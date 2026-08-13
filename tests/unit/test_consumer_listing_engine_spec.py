"""
Unit tests for Master Consumer Listing Engine Specification auditor.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scripts.constitution.check_consumer_listing_engine import (
    ConsumerListingEngineChecker,
    CONSUMER_LISTING_ENGINE_MAP,
)


def test_consumer_listing_engine_spec_auditor_report():
    checker = ConsumerListingEngineChecker(root_dir=root_dir)
    res = checker.audit_consumer_listing_engine()

    assert res["total_modules"] == 22
    assert res["verified_modules"] == 22
    assert res["score_pct"] == 100.0
    assert len(CONSUMER_LISTING_ENGINE_MAP) == 22

    # Test key modules across 18 UI components, Parallel Resolution, Security, Action Engine, and Caching
    assert CONSUMER_LISTING_ENGINE_MAP["CLE-CMP-01"] == "ProductCard Quick-Commerce Trust Card Component"
    assert CONSUMER_LISTING_ENGINE_MAP["CLE-CMP-05"] == "ProductDetail Full Detail View"
    assert CONSUMER_LISTING_ENGINE_MAP["CLE-CMP-06"] == "PriceDisplay MRP, Selling Price & Tax Transparency"
    assert CONSUMER_LISTING_ENGINE_MAP["CLE-CMP-08"] == "SellerVerificationBadge Licensed Seller Status"
    assert CONSUMER_LISTING_ENGINE_MAP["CLE-PIPE-01"] == "Parallel Resolution Pipeline (asyncio.gather)"
    assert CONSUMER_LISTING_ENGINE_MAP["CLE-ACT-01"] == "Server-Authoritative Action State Machine"
    assert CONSUMER_LISTING_ENGINE_MAP["CLE-CACHE-01"] == "Event-Driven Redis Cache Invalidation"
