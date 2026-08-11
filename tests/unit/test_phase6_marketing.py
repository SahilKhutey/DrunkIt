from datetime import datetime, timedelta, timezone

from app.domain.automation import (
    ABTestAllocator,
    Campaign,
    CampaignPlanner,
    Journey,
    JourneyStep,
    MessageTemplate,
)
from app.main import create_app


def test_campaign_planner_filters_by_segment_and_frequency_cap():
    now = datetime.now(timezone.utc)
    campaign = Campaign(
        code="winback",
        name="Winback",
        segment="at_risk",
        status="active",
        template=MessageTemplate(
            subject="We miss you, {{first_name}}",
            body="Come back for a responsible offer.",
            channel="email",
        ),
    )
    audience = [
        {"profile_id": "p1", "segments": ["at_risk"], "traits": {"first_name": "Asha"}},
        {"profile_id": "p2", "segments": ["loyal"], "traits": {"first_name": "Dev"}},
    ]
    planner = CampaignPlanner()

    first_plan = planner.eligible_recipients(campaign, audience, now=now)
    planner.mark_sent("winback", "p1", now)
    second_plan = planner.eligible_recipients(campaign, audience, now=now)

    assert first_plan == [
        {
            "profile_id": "p1",
            "campaign_code": "winback",
            "subject": "We miss you, Asha",
            "body": "Come back for a responsible offer.",
            "channel": "email",
        }
    ]
    assert second_plan == []


def test_ab_test_allocator_is_deterministic_for_same_subject():
    allocator = ABTestAllocator({"control": 50, "discount": 50})

    first = allocator.assign("profile-123", "promo-copy")
    second = allocator.assign("profile-123", "promo-copy")

    assert first == second
    assert first in {"control", "discount"}


def test_journey_schedules_active_steps_with_delays():
    triggered_at = datetime.now(timezone.utc)
    journey = Journey(
        code="onboarding",
        name="Onboarding",
        trigger_event="profile.created",
        status="active",
        steps=(
            JourneyStep("welcome", MessageTemplate("", "Welcome", "push")),
            JourneyStep("verify", MessageTemplate("", "Verify age", "sms"), delay=timedelta(hours=24)),
        ),
    )

    scheduled = journey.schedule_for("p1", triggered_at)

    assert [step["step_code"] for step in scheduled] == ["welcome", "verify"]
    assert scheduled[1]["send_at"] == triggered_at + timedelta(hours=24)


def test_marketing_app_exposes_phase6_routes():
    app = create_app()
    paths = {route.path for route in app.routes}

    assert "/api/v1/marketing/campaigns/plan" in paths
    assert "/api/v1/marketing/experiments/assign" in paths
    assert "/api/v1/marketing/journeys/schedule" in paths
