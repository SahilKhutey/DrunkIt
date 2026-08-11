"""
Pure-Python rule evaluation engine.

Evaluates a decision request against a set of policies and rules.
No I/O — pure functions — for full testability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from decimal import Decimal
from enum import Enum
from typing import Any


class DecisionOutcome(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"


@dataclass
class RuleHit:
    rule_id: str
    rule_name: str
    outcome: DecisionOutcome
    reason: str
    severity: str = "info"  # info|warning|critical
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationRequest:
    """A normalized request for compliance evaluation."""
    subject_type: str          # order|retailer|product|consumer
    subject_id: str
    jurisdiction_code: str
    requested_at: datetime
    actor: dict[str, Any]     # role, user_id, scope
    context: dict[str, Any]    # product, quantity, delivery_address, etc.
    policy_versions: dict[str, str] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    decision: DecisionOutcome
    confidence: float
    hits: list[RuleHit]
    matched_policies: list[str]
    evaluation_ms: int
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_allowed(self) -> bool:
        return self.decision == DecisionOutcome.ALLOW

    @property
    def is_denied(self) -> bool:
        return self.decision == DecisionOutcome.DENY

    @property
    def denial_reasons(self) -> list[str]:
        return [h.reason for h in self.hits if h.outcome == DecisionOutcome.DENY]

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "confidence": self.confidence,
            "hits": [
                {
                    "rule_id": h.rule_id,
                    "rule_name": h.rule_name,
                    "outcome": h.outcome.value,
                    "reason": h.reason,
                    "severity": h.severity,
                    "evidence": h.evidence,
                }
                for h in self.hits
            ],
            "matched_policies": self.matched_policies,
            "evaluation_ms": self.evaluation_ms,
            "metadata": self.metadata,
        }


# ==============================================================
# Rule functions — pure, testable
# ==============================================================

def _now_in_jurisdiction(req: EvaluationRequest) -> datetime:
    return req.requested_at.astimezone(timezone.utc)


def check_age_eligibility(req: EvaluationRequest, min_age: int) -> RuleHit:
    consumer_age = req.context.get("consumer_age")
    if consumer_age is None:
        return RuleHit(
            rule_id="age.unverified",
            rule_name="Age verification required",
            outcome=DecisionOutcome.DENY,
            reason="Consumer age not verified",
            severity="critical",
            evidence={"min_age": min_age},
        )
    if consumer_age < min_age:
        return RuleHit(
            rule_id="age.below_minimum",
            rule_name=f"Age below minimum ({min_age})",
            outcome=DecisionOutcome.DENY,
            reason=f"Consumer age {consumer_age} is below minimum {min_age}",
            severity="critical",
            evidence={"consumer_age": consumer_age, "min_age": min_age},
        )
    return RuleHit(
        rule_id="age.ok",
        rule_name="Age verified",
        outcome=DecisionOutcome.ALLOW,
        reason=f"Consumer age {consumer_age} >= {min_age}",
    )


def check_dry_day(req: EvaluationRequest, dry_dates: list[date]) -> RuleHit:
    request_date = req.requested_at.date()
    for d in dry_dates:
        if d == request_date:
            return RuleHit(
                rule_id="dry_day.active",
                rule_name="Dry day",
                outcome=DecisionOutcome.DENY,
                reason=f"Sales prohibited on dry day {d.isoformat()}",
                severity="critical",
                evidence={"date": d.isoformat()},
            )
    return RuleHit(
        rule_id="dry_day.ok",
        rule_name="No dry day",
        outcome=DecisionOutcome.ALLOW,
        reason="Not a dry day",
    )


def check_sales_hours(
    req: EvaluationRequest,
    permitted_hours: dict[str, Any],
) -> RuleHit:
    """permitted_hours: {start: "HH:MM", end: "HH:MM", days: [0-6]}"""
    now = _now_in_jurisdiction(req)
    current_time = now.time()
    current_day = now.weekday()

    start = time.fromisoformat(permitted_hours.get("start", "00:00"))
    end = time.fromisoformat(permitted_hours.get("end", "23:59"))
    days = permitted_hours.get("days", [0, 1, 2, 3, 4, 5, 6])

    if current_day not in days:
        return RuleHit(
            rule_id="hours.day_not_permitted",
            rule_name="Day not permitted",
            outcome=DecisionOutcome.DENY,
            reason=f"Sales not permitted on day {current_day}",
            severity="critical",
            evidence={"current_day": current_day, "permitted_days": days},
        )
    if not (start <= current_time <= end):
        return RuleHit(
            rule_id="hours.outside_window",
            rule_name="Outside sales hours",
            outcome=DecisionOutcome.DENY,
            reason=f"Current time {current_time} outside window {start}-{end}",
            severity="critical",
            evidence={"current_time": str(current_time), "window": f"{start}-{end}"},
        )
    return RuleHit(
        rule_id="hours.ok",
        rule_name="Within sales hours",
        outcome=DecisionOutcome.ALLOW,
        reason="Within permitted sales hours",
    )


def check_license_valid(req: EvaluationRequest, license_info: dict[str, Any]) -> RuleHit:
    status = license_info.get("status")
    valid_until_str = license_info.get("valid_until")
    if status != "ACTIVE":
        return RuleHit(
            rule_id="license.invalid_status",
            rule_name="License not active",
            outcome=DecisionOutcome.DENY,
            reason=f"License status: {status}",
            severity="critical",
            evidence={"status": status},
        )
    if valid_until_str:
        try:
            valid_until = datetime.fromisoformat(valid_until_str)
            if valid_until < req.requested_at:
                return RuleHit(
                    rule_id="license.expired",
                    rule_name="License expired",
                    outcome=DecisionOutcome.DENY,
                    reason=f"License expired on {valid_until.isoformat()}",
                    severity="critical",
                )
        except (ValueError, TypeError):
            return RuleHit(
                rule_id="license.unparseable",
                rule_name="License validity unparseable",
                outcome=DecisionOutcome.REVIEW,
                reason="Could not parse license validity date",
                severity="warning",
            )
    return RuleHit(
        rule_id="license.ok",
        rule_name="License valid",
        outcome=DecisionOutcome.ALLOW,
        reason="License is valid and active",
    )


def check_quantity_limit(
    req: EvaluationRequest,
    max_quantity: int | None,
    period: str = "order",
) -> RuleHit:
    quantity = req.context.get("quantity", 0)
    if max_quantity is None:
        return RuleHit(
            rule_id="quantity.no_limit",
            rule_name="No quantity limit",
            outcome=DecisionOutcome.ALLOW,
            reason="No quantity restriction",
        )
    if quantity > max_quantity:
        return RuleHit(
            rule_id=f"quantity.exceeded_{period}",
            rule_name=f"Quantity exceeds {period} limit",
            outcome=DecisionOutcome.DENY,
            reason=f"Quantity {quantity} exceeds max {max_quantity} per {period}",
            severity="critical",
            evidence={"quantity": quantity, "max": max_quantity, "period": period},
        )
    return RuleHit(
        rule_id="quantity.ok",
        rule_name="Quantity within limit",
        outcome=DecisionOutcome.ALLOW,
        reason="Quantity within permitted limit",
    )


def check_delivery_zone(
    req: EvaluationRequest,
    permitted_zones: list[str],
) -> RuleHit:
    zone = req.context.get("delivery_zone")
    if zone is None:
        return RuleHit(
            rule_id="zone.unknown",
            rule_name="Delivery zone unknown",
            outcome=DecisionOutcome.REVIEW,
            reason="Delivery zone not provided",
            severity="warning",
        )
    if zone not in permitted_zones:
        return RuleHit(
            rule_id="zone.not_permitted",
            rule_name="Delivery zone not permitted",
            outcome=DecisionOutcome.DENY,
            reason=f"Zone {zone} not in permitted zones",
            severity="critical",
            evidence={"zone": zone, "permitted": permitted_zones},
        )
    return RuleHit(
        rule_id="zone.ok",
        rule_name="Zone permitted",
        outcome=DecisionOutcome.ALLOW,
        reason="Delivery zone is permitted",
    )


def check_product_authorization(
    req: EvaluationRequest,
    product_info: dict[str, Any],
    jurisdiction_allowed_categories: list[str],
) -> RuleHit:
    category = product_info.get("category")
    if category not in jurisdiction_allowed_categories:
        return RuleHit(
            rule_id="product.not_authorized",
            rule_name="Product not authorized",
            outcome=DecisionOutcome.DENY,
            reason=f"Category {category} not authorized in this jurisdiction",
            severity="critical",
            evidence={"category": category, "allowed": jurisdiction_allowed_categories},
        )
    return RuleHit(
        rule_id="product.authorized",
        rule_name="Product authorized",
        outcome=DecisionOutcome.ALLOW,
        reason="Product category authorized",
    )



def aggregate_decision(hits: list[RuleHit]) -> tuple[DecisionOutcome, float]:
    """Aggregate rule hits into a final decision.

    Rules:
    - Any DENY → DENY (regardless of others)
    - No DENY but any REVIEW → REVIEW
    - All ALLOW → ALLOW
    """
    if any(h.outcome == DecisionOutcome.DENY for h in hits):
        return DecisionOutcome.DENY, 1.0
    if any(h.outcome == DecisionOutcome.REVIEW for h in hits):
        return DecisionOutcome.REVIEW, 0.7
    if all(h.outcome == DecisionOutcome.ALLOW for h in hits):
        return DecisionOutcome.ALLOW, 1.0
    return DecisionOutcome.REVIEW, 0.5


def evaluate_order(
    request: EvaluationRequest,
    *,
    min_age: int,
    dry_days: list[date],
    sales_hours: dict[str, Any],
    license_info: dict[str, Any],
    product_info: dict[str, Any],
    jurisdiction_categories: list[str],
    quantity_limit: int | None,
    permitted_zones: list[str],
) -> EvaluationResult:
    """Run all order-related checks and return a decision."""
    import time as _time
    start = _time.perf_counter()

    hits: list[RuleHit] = []
    hits.append(check_age_eligibility(request, min_age))
    hits.append(check_dry_day(request, dry_days))
    hits.append(check_sales_hours(request, sales_hours))
    hits.append(check_license_valid(request, license_info))
    hits.append(check_product_authorization(request, product_info, jurisdiction_categories))
    hits.append(check_quantity_limit(request, quantity_limit))
    hits.append(check_delivery_zone(request, permitted_zones))

    decision, confidence = aggregate_decision(hits)
    elapsed_ms = int((_time.perf_counter() - start) * 1000)

    return EvaluationResult(
        decision=decision,
        confidence=confidence,
        hits=hits,
        matched_policies=[
            "age_eligibility", "dry_days", "sales_hours",
            "license_validity", "product_authorization",
            "quantity_limit", "delivery_zone"
        ],
        evaluation_ms=elapsed_ms,
    )
