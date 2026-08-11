from typing import Tuple
from .models import EvaluatePolicyRequest, SystemRole, PrivacyClassification, BreakGlassLevel
from .sod_detector import check_sod_violation

def evaluate_abac_rules(req: EvaluatePolicyRequest) -> Tuple[str, str, str, bool]:
    s = req.subject
    r = req.resource
    a = req.action
    e = req.environment

    # 0. Break-Glass Override Check
    if s.break_glass_level != BreakGlassLevel.NONE:
        return "ALLOW", "BREAK_GLASS_OVERRIDE", f"Allowed under Emergency {s.break_glass_level}", False

    # Rule 4.1 — Geographic Containment
    if s.role in [SystemRole.STATE_ADMIN, SystemRole.DISTRICT_ADMIN, SystemRole.CITY_ADMIN, SystemRole.COMPLIANCE_OFFICER]:
        if len(s.assigned_jurisdictions) > 0 and r.jurisdiction not in s.assigned_jurisdictions:
            return "DENY", "RULE_4_1_GEO_CONTAINMENT", f"User jurisdiction {s.assigned_jurisdictions} does not match resource jurisdiction {r.jurisdiction}", False

    # Rule 4.3 — License Precedence
    if r.requires_license and r.license_status not in ["ACTIVE", "VERIFIED"]:
        return "DENY", "RULE_4_3_LICENSE_PRECEDENCE", f"Resource requires active license, but status is {r.license_status}", False

    # Rule 4.4 — P3 Identity Data Isolation
    if r.classification == PrivacyClassification.P3_IDENTITY_KYC:
        if s.role not in [SystemRole.DATA_PROTECTION_OFFICER, SystemRole.PLATFORM_ROOT, SystemRole.SUPER_ADMIN]:
            return "DENY", "RULE_4_4_P3_ISOLATION", "Access to P3 sensitive identity/KYC data is restricted to DPO & Identity Vault only", False

    # Rule 4.5 & 4.6 — SoD Matrix & 2-Man Rule Enforcement
    is_sod_conflict, sod_reason = check_sod_violation(s.user_id, r.resource_id, a.value)
    if is_sod_conflict:
        return "SOD_VIOLATION", "RULE_4_5_SOD_VIOLATION", sod_reason, False

    # Rule 4.7 — Consumer Self-Only
    if s.role in [SystemRole.GUEST, SystemRole.REGISTERED, SystemRole.IDENTITY_VERIFIED, SystemRole.AGE_ELIGIBLE, SystemRole.TRANSACTION_VERIFIED]:
        if r.resource_owner_id and r.resource_owner_id != s.user_id:
            return "DENY", "RULE_4_7_CONSUMER_SELF_ONLY", "Consumers are restricted to accessing their own resources only", False

    # Rule 4.8 — Device Trust Floor
    if s.device_trust_score < 70:
        return "CHALLENGE", "RULE_4_8_DEVICE_TRUST_FLOOR", f"Device trust score {s.device_trust_score} below floor 70. Step-up MFA required", True

    return "ALLOW", "ABAC_PASSED", "All ABAC policy rules passed", False
