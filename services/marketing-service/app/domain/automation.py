from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

Channel = Literal["email", "sms", "push", "in_app"]
CampaignStatus = Literal["draft", "scheduled", "active", "paused", "completed"]


@dataclass(frozen=True)
class MessageTemplate:
    subject: str
    body: str
    channel: Channel

    def render(self, traits: dict[str, Any]) -> dict[str, str]:
        rendered_subject = self.subject
        rendered_body = self.body
        for key, value in traits.items():
            token = "{{" + key + "}}"
            rendered_subject = rendered_subject.replace(token, str(value))
            rendered_body = rendered_body.replace(token, str(value))
        return {"subject": rendered_subject, "body": rendered_body, "channel": self.channel}


@dataclass(frozen=True)
class Campaign:
    code: str
    name: str
    segment: str
    template: MessageTemplate
    status: CampaignStatus = "draft"
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    frequency_cap_per_day: int = 1

    def is_sendable(self, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        if self.status != "active":
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True


@dataclass(frozen=True)
class JourneyStep:
    code: str
    template: MessageTemplate
    delay: timedelta = timedelta()
    exit_on_conversion: bool = True


@dataclass(frozen=True)
class Journey:
    code: str
    name: str
    trigger_event: str
    steps: tuple[JourneyStep, ...]
    status: CampaignStatus = "draft"

    def schedule_for(self, profile_id: str, triggered_at: datetime) -> list[dict[str, Any]]:
        if self.status != "active":
            return []
        return [
            {
                "profile_id": profile_id,
                "journey_code": self.code,
                "step_code": step.code,
                "send_at": triggered_at + step.delay,
                "channel": step.template.channel,
            }
            for step in self.steps
        ]


class ABTestAllocator:
    def __init__(self, variants: dict[str, int]) -> None:
        if not variants:
            raise ValueError("At least one variant is required")
        if any(weight <= 0 for weight in variants.values()):
            raise ValueError("Variant weights must be positive")
        self.variants = variants
        self._total_weight = sum(variants.values())

    def assign(self, subject_id: str, experiment_code: str) -> str:
        digest = hashlib.sha256(f"{experiment_code}:{subject_id}".encode("utf-8")).hexdigest()
        bucket = int(digest[:12], 16) % self._total_weight
        running = 0
        for variant, weight in self.variants.items():
            running += weight
            if bucket < running:
                return variant
        return next(reversed(self.variants))


class CampaignPlanner:
    def __init__(self) -> None:
        self._sent_log: dict[tuple[str, str, datetime], int] = {}

    def eligible_recipients(
        self,
        campaign: Campaign,
        audience: list[dict[str, Any]],
        *,
        now: datetime | None = None,
    ) -> list[dict[str, Any]]:
        now = now or datetime.now(timezone.utc)
        if not campaign.is_sendable(now):
            return []
        today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        recipients = []
        for profile in audience:
            profile_id = profile["profile_id"]
            sent_count = self._sent_log.get((campaign.code, profile_id, today), 0)
            if sent_count >= campaign.frequency_cap_per_day:
                continue
            if campaign.segment not in set(profile.get("segments", [])):
                continue
            message = campaign.template.render(profile.get("traits", {}))
            recipients.append({"profile_id": profile_id, "campaign_code": campaign.code, **message})
        return recipients

    def mark_sent(self, campaign_code: str, profile_id: str, sent_at: datetime | None = None) -> None:
        sent_at = sent_at or datetime.now(timezone.utc)
        today = datetime(sent_at.year, sent_at.month, sent_at.day, tzinfo=timezone.utc)
        key = (campaign_code, profile_id, today)
        self._sent_log[key] = self._sent_log.get(key, 0) + 1
