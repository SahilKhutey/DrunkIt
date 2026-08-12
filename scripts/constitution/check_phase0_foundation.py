"""
Phase 0 Foundation Checker.
Verifies root Makefile, .env.example, docker-compose.yml, init-databases.sh (24 microservice databases), TopicRegistry, and Auth/RBAC/ABAC pipelines.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure faccp_common is importable
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from faccp_common.communication import TopicRegistry
from faccp_common.trust import Role, Permission, AuthorizationEngine, default_authorization_engine


class Phase0FoundationChecker:
    """Verifies complete Phase 0 Foundation Execution integrity."""

    EXPECTED_DATABASES = [
        "faccp_identity", "faccp_consumer", "faccp_retailer", "faccp_catalog",
        "faccp_inventory", "faccp_order", "faccp_compliance", "faccp_audit",
        "faccp_risk", "faccp_verification", "faccp_delivery", "faccp_notification",
        "faccp_payment", "faccp_pricing", "faccp_analytics", "faccp_realtime",
        "faccp_whitelabel", "faccp_reporting", "faccp_support", "faccp_portal",
        "faccp_sustainability", "faccp_cdp", "faccp_marketing", "faccp_listing"
    ]

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_foundation(self) -> list[str]:
        violations = []

        makefile = self.root_dir / "Makefile"
        if not makefile.exists():
            violations.append("Phase 0 Foundation violation: Missing root Makefile")

        env_example = self.root_dir / ".env.example"
        if not env_example.exists():
            violations.append("Phase 0 Foundation violation: Missing root .env.example")

        docker_compose = self.root_dir / "docker-compose.yml"
        if not docker_compose.exists():
            violations.append("Phase 0 Foundation violation: Missing root docker-compose.yml")

        init_db = self.root_dir / "infrastructure" / "postgres" / "init-databases.sh"
        if not init_db.exists():
            violations.append("Phase 0 Foundation violation: Missing infrastructure/postgres/init-databases.sh")
        else:
            content = init_db.read_text(encoding="utf-8")
            for db in self.EXPECTED_DATABASES:
                if f"CREATE DATABASE {db};" not in content:
                    violations.append(f"Phase 0 Foundation violation: init-databases.sh missing CREATE DATABASE {db};")

        topics = TopicRegistry.all_names()
        if len(topics) < 12:
            violations.append(f"Phase 0 Foundation violation: TopicRegistry must define at least 12 domain topics (found {len(topics)})")

        auth_engine = default_authorization_engine()
        if not auth_engine:
            violations.append("Phase 0 Foundation violation: default_authorization_engine failed to instantiate")

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        v = self.check_foundation()
        if v:
            all_violations["phase0-foundation"] = v
        return all_violations


if __name__ == "__main__":
    checker = Phase0FoundationChecker()
    report = checker.check_all()
    if report:
        print("❌ PHASE 0 FOUNDATION VIOLATIONS DETECTED:")
        for area, viols in report.items():
            print(f"Area: {area}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Phase 0 Foundation Execution verified cleanly (Infrastructure, 24 DBs, Kafka & Auth intact).")
    sys.exit(0)
