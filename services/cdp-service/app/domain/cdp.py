from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Literal

ConsentScope = Literal["analytics", "personalization", "marketing", "third_party_export"]
SegmentCode = Literal[
    "new_customer",
    "high_value",
    "at_risk",
    "loyal",
    "dormant",
    "discount_sensitive",
]


def normalize_identifier(value: str) -> str:
    return value.strip().lower()


def stable_profile_id(identifier_type: str, identifier_value: str, salt: str = "faccp-cdp") -> str:
    material = f"{salt}:{identifier_type}:{normalize_identifier(identifier_value)}"
    return "cdp_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True)
class CDPEvent:
    profile_id: str
    event_type: str
    occurred_at: datetime
    properties: dict[str, Any] = field(default_factory=dict)
    value: Decimal = Decimal("0")


@dataclass
class CustomerProfile:
    profile_id: str
    identifiers: dict[str, set[str]] = field(default_factory=dict)
    traits: dict[str, Any] = field(default_factory=dict)
    events: list[CDPEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_identifier(self, identifier_type: str, value: str) -> None:
        self.identifiers.setdefault(identifier_type, set()).add(normalize_identifier(value))
        self.updated_at = datetime.now(timezone.utc)

    def merge(self, other: CustomerProfile) -> None:
        for identifier_type, values in other.identifiers.items():
            self.identifiers.setdefault(identifier_type, set()).update(values)
        self.traits = {**other.traits, **self.traits}
        self.events.extend(other.events)
        self.events.sort(key=lambda event: event.occurred_at)
        self.updated_at = datetime.now(timezone.utc)

    def record(self, event: CDPEvent) -> None:
        self.events.append(event)
        self.updated_at = datetime.now(timezone.utc)

    @property
    def order_count(self) -> int:
        return sum(1 for event in self.events if event.event_type == "order.completed")

    @property
    def lifetime_value(self) -> Decimal:
        return sum((event.value for event in self.events if event.event_type == "order.completed"), Decimal("0"))

    def days_since_last_order(self, now: datetime | None = None) -> int | None:
        now = now or datetime.now(timezone.utc)
        orders = [event for event in self.events if event.event_type == "order.completed"]
        if not orders:
            return None
        latest = max(event.occurred_at for event in orders)
        return max((now - latest).days, 0)


class IdentityGraph:
    def __init__(self) -> None:
        self._profiles: dict[str, CustomerProfile] = {}
        self._identifier_index: dict[tuple[str, str], str] = {}

    def resolve(self, identifiers: dict[str, str], traits: dict[str, Any] | None = None) -> CustomerProfile:
        if not identifiers:
            raise ValueError("At least one identifier is required")

        matched_profile_ids = {
            self._identifier_index[(identifier_type, normalize_identifier(value))]
            for identifier_type, value in identifiers.items()
            if (identifier_type, normalize_identifier(value)) in self._identifier_index
        }

        if matched_profile_ids:
            primary_id = sorted(matched_profile_ids)[0]
            primary = self._profiles[primary_id]
            for duplicate_id in sorted(matched_profile_ids - {primary_id}):
                duplicate = self._profiles.pop(duplicate_id)
                primary.merge(duplicate)
                for identifier_type, values in duplicate.identifiers.items():
                    for value in values:
                        self._identifier_index[(identifier_type, value)] = primary.profile_id
        else:
            identifier_type, identifier_value = sorted(identifiers.items())[0]
            primary_id = stable_profile_id(identifier_type, identifier_value)
            primary = CustomerProfile(profile_id=primary_id)
            self._profiles[primary_id] = primary

        for identifier_type, value in identifiers.items():
            normalized = normalize_identifier(value)
            primary.add_identifier(identifier_type, normalized)
            self._identifier_index[(identifier_type, normalized)] = primary.profile_id

        if traits:
            primary.traits.update(traits)
            primary.updated_at = datetime.now(timezone.utc)
        return primary

    def get(self, profile_id: str) -> CustomerProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise KeyError(f"Unknown CDP profile: {profile_id}") from exc

    def all_profiles(self) -> list[CustomerProfile]:
        return list(self._profiles.values())


class ConsentLedger:
    def __init__(self) -> None:
        self._grants: dict[str, set[ConsentScope]] = {}

    def grant(self, profile_id: str, scopes: set[ConsentScope]) -> None:
        self._grants.setdefault(profile_id, set()).update(scopes)

    def revoke(self, profile_id: str, scopes: set[ConsentScope]) -> None:
        self._grants.setdefault(profile_id, set()).difference_update(scopes)

    def has(self, profile_id: str, scope: ConsentScope) -> bool:
        return scope in self._grants.get(profile_id, set())

    def exportable(self, profiles: list[CustomerProfile], scope: ConsentScope) -> list[CustomerProfile]:
        return [profile for profile in profiles if self.has(profile.profile_id, scope)]


class SegmentEngine:
    def __init__(
        self,
        *,
        high_value_threshold: Decimal = Decimal("25000"),
        dormant_days: int = 90,
        at_risk_days: int = 45,
    ) -> None:
        self.high_value_threshold = high_value_threshold
        self.dormant_days = dormant_days
        self.at_risk_days = at_risk_days

    def assign(self, profile: CustomerProfile, now: datetime | None = None) -> set[SegmentCode]:
        now = now or datetime.now(timezone.utc)
        segments: set[SegmentCode] = set()
        days_since_last_order = profile.days_since_last_order(now)

        if profile.order_count == 0:
            segments.add("new_customer")
        if profile.lifetime_value >= self.high_value_threshold:
            segments.add("high_value")
        if profile.order_count >= 5 and days_since_last_order is not None and days_since_last_order <= 30:
            segments.add("loyal")
        if days_since_last_order is not None and self.at_risk_days <= days_since_last_order < self.dormant_days:
            segments.add("at_risk")
        if days_since_last_order is not None and days_since_last_order >= self.dormant_days:
            segments.add("dormant")
        if profile.traits.get("uses_promotions") is True:
            segments.add("discount_sensitive")

        return segments

    def build_audience(
        self,
        profiles: list[CustomerProfile],
        segment: SegmentCode,
        consent: ConsentLedger,
        scope: ConsentScope = "marketing",
        now: datetime | None = None,
    ) -> list[dict[str, Any]]:
        audience = []
        for profile in consent.exportable(profiles, scope):
            if segment not in self.assign(profile, now):
                continue
            audience.append(
                {
                    "profile_id": profile.profile_id,
                    "segments": sorted(self.assign(profile, now)),
                    "traits": dict(profile.traits),
                    "lifetime_value": str(profile.lifetime_value),
                    "order_count": profile.order_count,
                }
            )
        return audience
