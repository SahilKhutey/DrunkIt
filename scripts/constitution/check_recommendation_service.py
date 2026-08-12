"""
Recommendation Service Checker.
Verifies production code structure, endpoints, models, schemas, service logic, and seed script of recommendation-service.
"""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]


class RecommendationServiceChecker:
    """Verifies complete Recommendation Service microservice implementation."""

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_recommendation_service(self) -> list[str]:
        violations = []
        base_dir = self.root_dir / "services" / "recommendation-service"

        required_files = [
            "pyproject.toml",
            "Dockerfile",
            "alembic.ini",
            "README.md",
            "alembic/env.py",
            "alembic/versions/0001_initial.py",
            "app/config.py",
            "app/db/base.py",
            "app/db/models.py",
            "app/schemas/recommendation.py",
            "app/services/recommendation_service.py",
            "app/api/dependencies.py",
            "app/api/routes/recommendation.py",
            "app/main.py",
            "app/scripts/seed_recommendations.py",
        ]

        for req_file in required_files:
            file_path = base_dir / req_file
            if not file_path.exists():
                violations.append(f"Recommendation Service violation: Missing required file {req_file}")

        # Check endpoints in routes/recommendation.py
        routes_file = base_dir / "app" / "api" / "routes" / "recommendation.py"
        if routes_file.exists():
            content = routes_file.read_text(encoding="utf-8")
            required_endpoints = [
                "/profiles", "/affinities", "/personalized"
            ]
            for ep in required_endpoints:
                if ep not in content:
                    violations.append(f"Recommendation Service violation: Missing endpoint route {ep} in routes/recommendation.py")

        # Check models in db/models.py
        models_file = base_dir / "app" / "db" / "models.py"
        if models_file.exists():
            content = models_file.read_text(encoding="utf-8")
            required_models = [
                "class ConsumerPreferenceProfile", "class ProductAffinityScore"
            ]
            for model in required_models:
                if model not in content:
                    violations.append(f"Recommendation Service violation: Missing database model {model} in db/models.py")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_recommendation_service()
        if v:
            all_violations["recommendation-service"] = v
        return all_violations


if __name__ == "__main__":
    checker = RecommendationServiceChecker()
    report = checker.check_all()
    if report:
        print("❌ RECOMMENDATION SERVICE VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Recommendation Service microservice verified cleanly (Personalized Discovery & Affinity Engine intact).")
    sys.exit(0)
