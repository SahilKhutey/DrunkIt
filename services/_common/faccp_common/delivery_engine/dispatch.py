"""
Dispatch Engine & Driver Candidate Scorer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CandidateDriver:
    driver_id: str
    distance_km: float
    eta_minutes: float
    reliability_score: float = 0.95
    is_available: bool = True


class DriverScorer:
    """Calculates weighted dispatch score for candidate drivers."""

    @classmethod
    def score_driver(cls, driver: CandidateDriver) -> float:
        distance_score = max(0.0, 1.0 - (driver.distance_km / 10.0))
        eta_score = max(0.0, 1.0 - (driver.eta_minutes / 60.0))
        availability_score = 1.0 if driver.is_available else 0.0
        reliability_score = driver.reliability_score

        return (
            distance_score * 0.35 +
            eta_score * 0.30 +
            availability_score * 0.20 +
            reliability_score * 0.15
        )


class DispatchEngine:
    """Selects best candidate driver for delivery mission."""

    def select_best_driver(self, candidates: list[CandidateDriver]) -> CandidateDriver | None:
        eligible = [d for d in candidates if d.is_available]
        if not eligible:
            return None
        return max(eligible, key=DriverScorer.score_driver)
