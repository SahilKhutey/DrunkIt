"""
Automated Daily Constitution Audit Runner.
Executes nightly audits for compliance, retention, secrets, and policy drift.
"""

from __future__ import annotations

import asyncio
from datetime import date
import json
import sys
from pathlib import Path

# Ensure root is in path
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(root_dir / "services" / "_common") not in sys.path:
    sys.path.insert(0, str(root_dir / "services" / "_common"))

from scripts.constitution.check_compliance import ConstitutionChecker



class DailyConstitutionAudit:
    """Daily audit engine for continuous compliance monitoring."""

    def __init__(self) -> None:
        self.checker = ConstitutionChecker(root_dir=str(root_dir))

    async def run(self) -> dict:
        print(f"Starting Daily Constitution Audit for {date.today().isoformat()}...")
        
        compliance_report = self.checker.check_all()
        
        audit_summary = {
            "audit_date": date.today().isoformat(),
            "constitution_compliance": compliance_report,
            "status": "HEALTHY" if compliance_report["failed"] == 0 else "VIOLATIONS_DETECTED",
        }

        output_dir = root_dir / "docs" / "audit_reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        report_file = output_dir / f"daily_audit_{date.today().isoformat()}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(audit_summary, f, indent=2)

        print(f"Audit completed. Compliance Score: {compliance_report['compliance_score_pct']}%. Report written to {report_file}")
        return audit_summary


if __name__ == "__main__":
    audit = DailyConstitutionAudit()
    asyncio.run(audit.run())
