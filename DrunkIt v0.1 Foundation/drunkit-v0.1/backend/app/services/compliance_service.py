"""Deterministic regulatory and policy compliance engine for Indian alcohol commerce."""

import os
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.db.uow import SyncUnitOfWork
from app.models.compliance import ComplianceCheck, ComplianceDecision
from app.models.retailer import Jurisdiction, Retailer, RetailerLicence, RetailerLocation
from app.schemas.compliance import (
    ComplianceCheckRequest,
    ComplianceDecisionResponse,
    JurisdictionPolicySummary,
)

# Base path for jurisdictional policies
POLICIES_DIR = Path(__file__).resolve().parent.parent.parent / "policies" / "jurisdictions"


class PolicyRegistry:
    """Registry caching and loading versioned jurisdictional YAML policies."""

    _cache: dict[str, dict[str, Any]] = {}

    @classmethod
    def load_policy(cls, jurisdiction_code: str) -> dict[str, Any]:
        """Load and parse policy for a given state jurisdiction code (e.g. 'IN-WB' or 'WB')."""
        normalized_code = jurisdiction_code.strip().upper()
        if not normalized_code.startswith("IN-"):
            normalized_code = f"IN-{normalized_code}"

        if normalized_code in cls._cache:
            return cls._cache[normalized_code]

        policy_file = POLICIES_DIR / f"{normalized_code}.yaml"
        if not policy_file.exists():
            # Fallback default policy
            fallback_policy = {
                "jurisdiction_code": normalized_code,
                "jurisdiction_name": normalized_code,
                "version": "2026.1-DEFAULT",
                "timezone": "Asia/Kolkata",
                "legal_drinking_age": {"spirits": 21, "beer": 21, "wine": 21},
                "channels": {
                    "in_store": {"allowed": True},
                    "online_ordering": {"allowed": False},
                    "home_delivery": {"allowed": False},
                },
                "operating_hours": {"open_time": "10:00", "close_time": "22:00"},
                "possession_limits_ml": {"spirits": 4500, "beer": 18000, "wine": 9000},
                "dry_days_recurring": ["01-26", "08-15", "10-02"],
                "mandatory_checks": {"age_verification": True},
            }
            cls._cache[normalized_code] = fallback_policy
            return fallback_policy

        with open(policy_file, encoding="utf-8") as f:
            policy_data = yaml.safe_load(f)
            cls._cache[normalized_code] = policy_data
            return policy_data

    @classmethod
    def list_summaries(cls) -> list[JurisdictionPolicySummary]:
        """List all available state policy summaries."""
        summaries = []
        if POLICIES_DIR.exists():
            for p_file in POLICIES_DIR.glob("IN-*.yaml"):
                code = p_file.stem
                policy = cls.load_policy(code)
                summaries.append(
                    JurisdictionPolicySummary(
                        jurisdiction_code=policy["jurisdiction_code"],
                        jurisdiction_name=policy.get("jurisdiction_name", code),
                        version=policy.get("version", "1.0"),
                        legal_drinking_age=policy.get("legal_drinking_age", {}),
                        channels=policy.get("channels", {}),
                        operating_hours=policy.get("operating_hours", {}),
                        possession_limits_ml=policy.get("possession_limits_ml", {}),
                        dry_days_count=len(policy.get("dry_days_recurring", [])),
                    )
                )
        return summaries


class ComplianceService:
    """Deterministic policy compliance evaluator."""

    @staticmethod
    def _parse_time(time_str: str) -> time:
        """Parse HH:MM string into datetime.time."""
        parts = [int(p) for p in time_str.split(":")]
        return time(hour=parts[0], minute=parts[1])

    @classmethod
    def evaluate_compliance(
        cls,
        request: ComplianceCheckRequest,
        uow: SyncUnitOfWork,
    ) -> ComplianceDecisionResponse:
        """Perform comprehensive, fail-closed deterministic policy checks."""
        session = uow.session
        now = request.current_time or datetime.now(timezone.utc)
        policy = PolicyRegistry.load_policy(request.jurisdiction_code)
        normalized_jur_code = policy["jurisdiction_code"]

        # Convert UTC now to jurisdiction local timezone if specified
        tz_name = policy.get("timezone", "Asia/Kolkata")
        try:
            if now.tzinfo is None:
                local_now = now.replace(tzinfo=ZoneInfo(tz_name))
            else:
                local_now = now.astimezone(ZoneInfo(tz_name))
        except Exception:
            local_now = now

        # 1. Resolve Jurisdiction Model
        state_code_part = normalized_jur_code.replace("IN-", "")
        jurisdiction = session.scalars(
            select(Jurisdiction).where(
                Jurisdiction.country_code == "IN",
                Jurisdiction.state_code == state_code_part,
            )
        ).first()

        if not jurisdiction:
            jurisdiction = Jurisdiction(
                country_code="IN",
                state_code=state_code_part,
                name=policy.get("jurisdiction_name", normalized_jur_code),
            )
            session.add(jurisdiction)
            session.flush()

        denial_reasons: list[str] = []
        required_checks: list[str] = []

        # -------------------------------------------------------------
        # Rule 1: Legal Drinking Age (LDA)
        # -------------------------------------------------------------
        lda_rules = policy.get("legal_drinking_age", {})
        p_class = request.product_class.lower()
        min_age = lda_rules.get(p_class, lda_rules.get("spirits", 21))

        if request.consumer_age is None:
            required_checks.append("AGE_VERIFICATION_REQUIRED")
        elif not request.is_age_verified:
            required_checks.append("AGE_VERIFICATION_REQUIRED")
            if request.consumer_age < min_age:
                denial_reasons.append("UNDERAGE_DENIED")
        elif request.consumer_age < min_age:
            denial_reasons.append("UNDERAGE_DENIED")

        # -------------------------------------------------------------
        # Rule 2: Dry Day Calendar Check
        # -------------------------------------------------------------
        month_day = local_now.strftime("%m-%d")
        dry_days = policy.get("dry_days_recurring", [])
        if month_day in dry_days:
            denial_reasons.append("DRY_DAY_DENIED")

        # -------------------------------------------------------------
        # Rule 3: Permitted Operating Hours
        # -------------------------------------------------------------
        hours = policy.get("operating_hours", {})
        if "open_time" in hours and "close_time" in hours:
            open_t = cls._parse_time(hours["open_time"])
            close_t = cls._parse_time(hours["close_time"])
            current_t = local_now.time()
            if not (open_t <= current_t <= close_t):
                denial_reasons.append("OUTSIDE_OPERATING_HOURS")

        # -------------------------------------------------------------
        # Rule 4: Channel Eligibility (In-Store, Ordering, Delivery)
        # -------------------------------------------------------------
        channels = policy.get("channels", {})
        channel_norm = request.channel.strip().upper()

        if channel_norm in ["HOME_DELIVERY", "DELIVERY"]:
            del_cfg = channels.get("home_delivery", {})
            if not del_cfg.get("allowed", False):
                denial_reasons.append("DELIVERY_PROHIBITED_IN_JURISDICTION")
        elif channel_norm == "ONLINE_ORDER":
            order_cfg = channels.get("online_ordering", {})
            if not order_cfg.get("allowed", False):
                denial_reasons.append("ONLINE_ORDERING_PROHIBITED_IN_JURISDICTION")

        # -------------------------------------------------------------
        # Rule 5: Maximum Possession / Transaction Limits
        # -------------------------------------------------------------
        limits = policy.get("possession_limits_ml", {})
        max_vol = limits.get(p_class, limits.get("spirits", 4500))
        if request.total_volume_ml > max_vol:
            denial_reasons.append("POSSESSION_LIMIT_EXCEEDED")

        # -------------------------------------------------------------
        # Rule 6: Retailer Licence Verification
        # -------------------------------------------------------------
        if request.retailer_id or request.retailer_location_id:
            ret_id = request.retailer_id
            if not ret_id and request.retailer_location_id:
                loc = session.get(RetailerLocation, request.retailer_location_id)
                if loc:
                    ret_id = loc.retailer_id

            if ret_id:
                licence = session.scalars(
                    select(RetailerLicence).where(
                        RetailerLicence.retailer_id == ret_id,
                        RetailerLicence.jurisdiction_id == jurisdiction.id,
                        RetailerLicence.status == "ACTIVE",
                    )
                ).first()
                if not licence:
                    denial_reasons.append("RETAILER_LICENCE_INVALID")

        # -------------------------------------------------------------
        # Decision Synthesis
        # -------------------------------------------------------------
        if denial_reasons:
            decision_str = "DENIED"
            final_reasons = denial_reasons
        elif required_checks:
            decision_str = "REQUIRES_VERIFICATION"
            final_reasons = ["PENDING_VERIFICATION_REQUIREMENTS"]
        else:
            decision_str = "ALLOWED"
            final_reasons = ["COMPLIANCE_SATISFIED"]

        # Persist Compliance Check & Decision Records
        check = ComplianceCheck(
            correlation_id=request.correlation_id,
            consumer_id=request.consumer_id,
            jurisdiction_id=jurisdiction.id,
            product_id=request.product_id,
            retailer_id=request.retailer_id,
            context_json={
                "channel": request.channel,
                "consumer_age": request.consumer_age,
                "is_age_verified": request.is_age_verified,
                "quantity": request.quantity,
                "total_volume_ml": request.total_volume_ml,
                "product_class": request.product_class,
                "time": local_now.isoformat(),
            },
        )
        session.add(check)
        session.flush()

        decision = ComplianceDecision(
            compliance_check_id=check.id,
            decision=decision_str,
            reason_codes=final_reasons,
            required_checks=required_checks,
            rule_set_version=policy.get("version", "1.0"),
        )
        session.add(decision)
        session.flush()

        # Publish Outbox Event
        uow.publish_outbox(
            event_type="COMPLIANCE_EVALUATED",
            aggregate_type="ComplianceDecision",
            aggregate_id=decision.id,
            correlation_id=request.correlation_id,
            payload={
                "decision": decision_str,
                "reasons": final_reasons,
                "required_checks": required_checks,
                "jurisdiction": normalized_jur_code,
            },
        )

        return ComplianceDecisionResponse(
            check_id=check.id,
            correlation_id=request.correlation_id,
            jurisdiction_code=normalized_jur_code,
            decision=decision_str,
            reason_codes=final_reasons,
            required_checks=required_checks,
            rule_set_version=decision.rule_set_version,
            decided_at=decision.decided_at,
        )
