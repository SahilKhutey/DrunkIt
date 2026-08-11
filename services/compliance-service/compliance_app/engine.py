import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
from .models import ComplianceEvaluationRequest, DecisionResult

POLICIES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../policies/jurisdictions/india/states")
)

def load_policy(jurisdiction: str) -> dict:
    mapping = {
        "IN-KA": "karnataka.json",
        "IN-MH": "maharashtra.json",
        "IN-DL": "delhi.json"
    }
    filename = mapping.get(jurisdiction, "karnataka.json")
    filepath = os.path.join(POLICIES_DIR, filename)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Fallback default rule set if file not loaded
    return {
        "jurisdictionId": jurisdiction,
        "name": "Default National Fallback Policy",
        "version": "1.0",
        "legalDrinkingAge": 21,
        "permittedHours": {"start": "10:00", "end": "22:00"},
        "maxPerTransactionVolumeMl": 9000,
        "prohibitedDays": ["2026-10-02", "2026-01-26", "2026-08-15"]
    }

def evaluate_compliance(req: ComplianceEvaluationRequest) -> Tuple[DecisionResult, List[str], str]:
    policy = load_policy(req.jurisdiction)
    reasons = []

    # 1. Consumer Age Eligibility Check
    if not req.consumer_age_eligible:
        reasons.append("Consumer is not age-eligible for alcohol purchase in this jurisdiction")

    # 2. License Status Check
    if req.license_status not in ["ACTIVE", "VERIFIED"]:
        reasons.append(f"Store excise license is invalid or inactive ({req.license_status})")

    # 3. Dry Days / Prohibited Days Check
    order_dt = datetime.fromisoformat(req.order_timestamp_iso.replace("Z", "+00:00"))
    date_str = order_dt.strftime("%Y-%m-%d")
    prohibited_days = policy.get("prohibitedDays", [])
    if date_str in prohibited_days:
        reasons.append(f"Order attempt on prohibited dry day ({date_str}) in {req.jurisdiction}")

    # 4. Trading Hours Check
    permitted_hours = policy.get("permittedHours", {})
    start_time = permitted_hours.get("start", "10:00")
    end_time = permitted_hours.get("end", "22:00")
    time_str = order_dt.strftime("%H:%M")
    if not (start_time <= time_str <= end_time):
        reasons.append(f"Order outside permitted store hours ({start_time} - {end_time}) in {req.jurisdiction}")

    # 5. Volume Limit Check
    total_volume_ml = sum(item.volume_ml * item.quantity for item in req.items)
    max_volume = policy.get("maxPerTransactionVolumeMl", 9000)
    if total_volume_ml > max_volume:
        reasons.append(f"Order total volume ({total_volume_ml}ml) exceeds maximum transaction limit ({max_volume}ml)")

    if len(reasons) > 0:
        return DecisionResult.DENY, reasons, policy.get("version", "1.0")

    return DecisionResult.ALLOW, ["All regulatory compliance checks passed successfully"], policy.get("version", "1.0")
