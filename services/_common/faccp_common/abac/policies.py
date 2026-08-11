"""
Default ABAC policies for FACCP.
"""

from __future__ import annotations

from faccp_common.abac.engine import (
    Policy, PolicyRule, PolicyEffect,
    and_, or_, not_,
    eq, ne, in_, not_in, ge, contains,
)


def _action_in(actions: list[str]):
    def check(req) -> bool:
        return req.action.action in actions
    return check


GLOBAL_POLICIES = [
    Policy(
        policy_id="GLOBAL-LOCK",
        name="Account lock check",
        description="Locked users cannot do anything except login/unlock",
        rules=[
            PolicyRule(
                rule_id="GLOBAL-LOCK-DENY",
                description="Locked users are denied all access except authentication",
                effect=PolicyEffect.DENY,
                conditions=[
                    eq("subject.is_locked", True),
                    not_in("subject.primary_role", ["PLATFORM_ROOT"]),
                    not_(_action_in(["auth.login", "auth.unlock"])),
                ],
                priority=1000,
            ),
        ],
    ),
    Policy(
        policy_id="GLOBAL-INACTIVE",
        name="Account active check",
        description="Inactive users cannot do anything",
        rules=[
            PolicyRule(
                rule_id="GLOBAL-INACTIVE-DENY",
                description="Inactive users are denied all access",
                effect=PolicyEffect.DENY,
                conditions=[
                    eq("subject.is_active", False),
                    ne("subject.primary_role", "PLATFORM_ROOT"),
                ],
                priority=999,
            ),
        ],
    ),
]


RESOURCE_POLICIES = [
    Policy(
        policy_id="CONSUMER-OWN",
        name="Consumer owns their own data",
        description="Consumers can read/update their own profile",
        rules=[
            PolicyRule(
                rule_id="CONSUMER-OWN-READ",
                description="Consumer can read their own profile",
                effect=PolicyEffect.PERMIT,
                conditions=[
                    eq("resource.resource_type", "consumer"),
                    eq("action.action", "read"),
                    eq("subject.user_id", "resource.owner_id"),
                ],
            ),
            PolicyRule(
                rule_id="CONSUMER-OWN-UPDATE",
                description="Consumer can update their own profile",
                effect=PolicyEffect.PERMIT,
                conditions=[
                    eq("resource.resource_type", "consumer"),
                    in_("action.action", ["update", "partial_update"]),
                    eq("subject.user_id", "resource.owner_id"),
                ],
                obligations=["audit_log"],
            ),
        ],
    ),
    Policy(
        policy_id="CONSUMER-PII-ISOLATION",
        name="Sensitive consumer data is restricted",
        description="Only authorized roles can access P3 (sensitive) consumer data",
        rules=[
            PolicyRule(
                rule_id="P3-ISOLATION",
                description="Deny non-DPO access to P3 data",
                effect=PolicyEffect.DENY,
                conditions=[
                    eq("resource.classification", "P3"),
                    not_in("subject.primary_role", [
                        "PLATFORM_ROOT", "DATA_PROTECTION_OFFICER",
                        "SUPER_ADMIN", "SECURITY_ADMIN",
                    ]),
                    in_("action.action", ["read", "export"]),
                ],
                priority=500,
            ),
        ],
    ),
    Policy(
        policy_id="ORDER-CONSUMER",
        name="Consumers see their own orders",
        description="Consumers can read their own orders; retailers see orders for their store",
        rules=[
            PolicyRule(
                rule_id="ORDER-CONSUMER-READ",
                description="Consumer can read their own orders",
                effect=PolicyEffect.PERMIT,
                conditions=[
                    eq("resource.resource_type", "order"),
                    eq("action.action", "read"),
                    eq("subject.user_id", "resource.owner_id"),
                ],
            ),
            PolicyRule(
                rule_id="ORDER-RETAILER-READ",
                description="Retailer staff can read orders for assigned stores",
                effect=PolicyEffect.PERMIT,
                conditions=[
                    eq("resource.resource_type", "order"),
                    eq("action.action", "read"),
                    in_("subject.primary_role", ["STORE_MANAGER", "ORDER_MANAGER", "PACKER", "RETAILER_OWNER", "ORG_ADMIN"]),
                    contains("subject.assigned_stores", "resource.store_id"),
                ],
            ),
            PolicyRule(
                rule_id="ORDER-DRIVER-READ",
                description="Drivers can read their assigned orders",
                effect=PolicyEffect.PERMIT,
                conditions=[
                    eq("resource.resource_type", "order"),
                    eq("action.action", "read"),
                    in_("subject.primary_role", ["DELIVERY_AGENT", "SENIOR_AGENT", "JUNIOR_AGENT"]),
                    eq("subject.user_id", "resource.owner_id"),
                ],
            ),
        ],
    ),
    Policy(
        policy_id="LICENSE-JURISDICTION",
        name="Licenses are bound to issuing jurisdiction",
        description="Admins can only manage licenses in their jurisdiction",
        rules=[
            PolicyRule(
                rule_id="LICENSE-STATE-ADMIN",
                description="State admins can verify licenses in their state",
                effect=PolicyEffect.PERMIT,
                conditions=[
                    eq("resource.resource_type", "license"),
                    in_("action.action", ["verify", "approve", "read"]),
                    in_("subject.primary_role", ["STATE_ADMIN", "REGULATORY_ADMIN", "ZONAL_LICENSING_OFFICER", "EXCISE_INSPECTOR"]),
                    contains("subject.assigned_jurisdictions", "resource.jurisdiction"),
                ],
            ),
            PolicyRule(
                rule_id="LICENSE-OUTSIDE-JURISDICTION-DENY",
                description="Admins cannot act on licenses outside their jurisdiction",
                effect=PolicyEffect.DENY,
                conditions=[
                    eq("resource.resource_type", "license"),
                    in_("subject.primary_role", ["STATE_ADMIN", "ZONAL_LICENSING_OFFICER", "EXCISE_INSPECTOR"]),
                    not_(contains("subject.assigned_jurisdictions", "resource.jurisdiction")),
                    in_("action.action", ["verify", "approve", "suspend", "revoke"]),
                ],
                priority=400,
            ),
        ],
    ),
    Policy(
        policy_id="AUDIT-RESTRICTED",
        name="Audit data is read-only for auditors",
        description="Auditors can read and export, but never modify audit data",
        rules=[
            PolicyRule(
                rule_id="AUDIT-READ",
                description="Auditors can read audit data",
                effect=PolicyEffect.PERMIT,
                conditions=[
                    eq("resource.resource_type", "audit_event"),
                    in_("action.action", ["read", "search", "verify"]),
                    in_("subject.primary_role", ["AUDITOR", "INTERNAL_AUDITOR", "EXTERNAL_AUDITOR", "SUPER_ADMIN", "SECURITY_ADMIN"]),
                ],
            ),
            PolicyRule(
                rule_id="AUDIT-MODIFY-DENY",
                description="Audit data is append-only — no modifications allowed",
                effect=PolicyEffect.DENY,
                conditions=[
                    eq("resource.resource_type", "audit_event"),
                    in_("action.action", ["update", "delete", "create"]),
                    ne("subject.primary_role", "PLATFORM_ROOT"),
                ],
                priority=900,
            ),
        ],
    ),
    Policy(
        policy_id="PII-ACCESS",
        name="PII access requires legitimate purpose and audit",
        description="P3 (sensitive PII) access is tightly controlled",
        rules=[
            PolicyRule(
                rule_id="PII-DPO-ONLY",
                description="Only DPO can read raw P3 data",
                effect=PolicyEffect.PERMIT,
                conditions=[
                    eq("resource.classification", "P3"),
                    in_("subject.primary_role", ["DATA_PROTECTION_OFFICER", "PLATFORM_ROOT"]),
                    eq("action.action", "read"),
                ],
                obligations=["audit_log", "mfa_required", "purpose_required"],
            ),
        ],
    ),
    Policy(
        policy_id="RISK-BLOCK",
        name="High-risk users are blocked from sensitive actions",
        description="Users with risk score >= 80 cannot make payments or sensitive changes",
        rules=[
            PolicyRule(
                rule_id="RISK-BLOCK-PAYMENTS",
                description="High-risk users blocked from payment actions",
                effect=PolicyEffect.DENY,
                conditions=[
                    ge("subject.risk_score", 80),
                    in_("action.action", ["create", "approve"]),
                    in_("resource.resource_type", ["payment", "refund", "settlement"]),
                ],
                priority=800,
            ),
        ],
    ),
    Policy(
        policy_id="2MAN-RULE",
        name="Critical actions require 2-person integrity",
        description="High-impact actions require 2 distinct approvers",
        rules=[
            PolicyRule(
                rule_id="2MAN-REQUIRED",
                description="Critical financial actions require SoD",
                effect=PolicyEffect.DENY,
                conditions=[
                    eq("action.requires_2man", True),
                    eq("action.action", "approve"),
                    eq("environment.custom.requester_id", "subject.user_id"),
                ],
                priority=950,
            ),
        ],
    ),
]


def build_default_policies() -> list[Policy]:
    return GLOBAL_POLICIES + RESOURCE_POLICIES


DEFAULT_POLICIES = build_default_policies()
