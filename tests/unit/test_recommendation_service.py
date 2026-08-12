"""
Unit tests for Phase 10 Recommendation Service (Schemas, Profiles, Affinities, and Static Checker).
"""

from __future__ import annotations

import os
import sys
import pytest
from pydantic import ValidationError

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
service_path = os.path.join(root_dir, "services/recommendation-service")
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

from app.schemas.recommendation import PreferenceProfileCreate, AffinityScoreCreate
from scripts.constitution.check_recommendation_service import RecommendationServiceChecker


def test_preference_profile_create_valid():
    prof = PreferenceProfileCreate(
        consumer_id="usr_consumer_101",
        preferred_categories=["WHISKY"],
        preferred_brands=["GLENFIDDICH"],
        price_sensitivity_score=0.4,
    )
    assert prof.consumer_id == "usr_consumer_101"


def test_affinity_score_create_valid():
    aff = AffinityScoreCreate(
        sku_id_a="SKU_A",
        sku_id_b="SKU_B",
        affinity_score=0.85,
    )
    assert aff.affinity_score == 0.85


def test_recommendation_service_checker():
    checker = RecommendationServiceChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
