"""
Domain Isolation Checker (§9.1 & §9.2).
AST-based static analyzer verifying zero direct cross-domain DB model imports and database connection URL violations.
"""

from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path


class DomainIsolationChecker:
    """Verifies no service imports another service's internal classes or foreign database URLs."""

    SERVICE_TO_OWN_DB: dict[str, str] = {
        "identity-service": "faccp_identity",
        "consumer-service": "faccp_consumer",
        "retailer-service": "faccp_retailer",
        "catalog-service": "faccp_catalog",
        "inventory-service": "faccp_inventory",
        "order-service": "faccp_order",
        "compliance-service": "faccp_compliance",
        "audit-service": "faccp_audit",
        "risk-service": "faccp_risk",
        "verification-service": "faccp_verification",
        "delivery-service": "faccp_delivery",
        "notification-service": "faccp_notification",
        "payment-service": "faccp_payment",
        "pricing-service": "faccp_pricing",
        "analytics-service": "faccp_analytics",
        "realtime-service": "faccp_realtime",
        "whitelabel-service": "faccp_whitelabel",
        "compliance-reporting-service": "faccp_reporting",
        "support-agent": "faccp_support",
        "developer-portal": "faccp_portal",
        "sustainability-service": "faccp_sustainability",
        "cdp-service": "faccp_cdp",
        "marketing-service": "faccp_marketing",
    }

    def __init__(self, root_dir: str | None = None) -> None:
        self.root_dir = Path(root_dir or Path(__file__).resolve().parents[2])

    def check_file(self, file_path: Path) -> list[str]:
        violations = []
        rel_path = file_path.relative_to(self.root_dir)
        parts = rel_path.parts

        if len(parts) < 2 or parts[0] != "services" or parts[1] == "_common":
            return violations

        service_name = parts[1]
        own_db = self.SERVICE_TO_OWN_DB.get(service_name)

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return violations

        # 1. AST import check for cross-service internal model imports
        try:
            tree = ast.parse(content, filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = getattr(node, "module", "") or ""
                    if module.startswith("services."):
                        target_service = module.split(".")[1]
                        if target_service != service_name and target_service != "_common":
                            violations.append(
                                f"{rel_path}: Imports {module} — cross-domain direct import forbidden (§9.1)"
                            )
        except SyntaxError:
            pass

        # 2. Foreign database URL connection check
        if own_db and ("config" in file_path.name or "settings" in file_path.name or "env" in file_path.name):
            for match in re.finditer(r'(\w*_?DB_URL|database_url)\s*=\s*["\']([^"\']+)["\']', content):
                url = match.group(2)
                for other_service, foreign_db in self.SERVICE_TO_OWN_DB.items():
                    if foreign_db != own_db and foreign_db in url:
                        violations.append(
                            f"{rel_path}: References foreign database '{foreign_db}' — must only connect to '{own_db}' (§9.2)"
                        )

        return violations

    def check_all(self) -> dict[str, list[str]]:
        all_violations: dict[str, list[str]] = {}
        services_dir = self.root_dir / "services"
        if not services_dir.exists():
            return all_violations

        for py_file in services_dir.rglob("*.py"):
            if "tests" in py_file.parts or "_common" in py_file.parts:
                continue
            violations = self.check_file(py_file)
            if violations:
                service_name = py_file.relative_to(services_dir).parts[0]
                all_violations.setdefault(service_name, []).extend(violations)

        return all_violations


if __name__ == "__main__":
    checker = DomainIsolationChecker()
    report = checker.check_all()
    if report:
        print("❌ DOMAIN ISOLATION VIOLATIONS DETECTED:")
        for service, viols in report.items():
            print(f"Service: {service}")
            for v in viols:
                print(f"  └── {v}")
        sys.exit(1)
    print("✅ Domain Isolation Protocol verified cleanly (no cross-DB or cross-service imports).")
    sys.exit(0)
