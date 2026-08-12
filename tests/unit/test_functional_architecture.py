"""
Unit tests for Functional Architecture (13 Domains, 71 Modules, 12 Phases).
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
common_path = os.path.join(root_dir, "services/_common")
if common_path not in sys.path:
    sys.path.insert(0, common_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from faccp_common.architecture import DomainRegistry, FunctionalArchitecture
from scripts.constitution.check_functional_architecture import FunctionalArchitectureChecker


def test_domain_registry_counts():
    assert len(DomainRegistry.DOMAINS) == 13
    total_modules = sum(len(mods) for mods in DomainRegistry.DOMAINS.values())
    assert total_modules == 71


def test_development_phases():
    assert 0 in FunctionalArchitecture.DEVELOPMENT_PHASES
    assert 12 in FunctionalArchitecture.DEVELOPMENT_PHASES
    assert "PLT-01" in FunctionalArchitecture.DEVELOPMENT_PHASES[0]
    assert "CMP-01" in FunctionalArchitecture.DEVELOPMENT_PHASES[3]


def test_functional_architecture_checker():
    checker = FunctionalArchitectureChecker(root_dir=root_dir)
    report = checker.check_all()
    assert len(report) == 0
