from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from app.domain.automation import (
    ABTestAllocator,
    Campaign,
    CampaignPlanner,
    Journey,
    JourneyStep,
    MessageTemplate,
)
from app.schemas import ABTestRequest, AudiencePlanRequest, JourneyScheduleRequest


def _template(payload: Any) -> MessageTemplate:
    return MessageTemplate(subject=payload.subject, body=payload.body, channel=payload.channel)


def _campaign(payload: Any) -> Campaign:
    return Campaign(
        code=payload.code,
        name=payload.name,
        segment=payload.segment,
        template=_template(payload.template),
        status=payload.status,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        frequency_cap_per_day=payload.frequency_cap_per_day,
    )


def create_app() -> FastAPI:
    app = FastAPI(title="FACCP Marketing Service", version="0.1.0")
    planner = CampaignPlanner()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "faccp-marketing"}

    @app.post("/api/v1/marketing/campaigns/plan")
    async def plan_campaign(payload: AudiencePlanRequest) -> dict[str, Any]:
        recipients = planner.eligible_recipients(_campaign(payload.campaign), payload.audience, now=payload.now)
        return {"count": len(recipients), "items": recipients}

    @app.post("/api/v1/marketing/experiments/assign")
    async def assign_variant(payload: ABTestRequest) -> dict[str, str]:
        allocator = ABTestAllocator(payload.variants)
        return {
            "experiment_code": payload.experiment_code,
            "subject_id": payload.subject_id,
            "variant": allocator.assign(payload.subject_id, payload.experiment_code),
        }

    @app.post("/api/v1/marketing/journeys/schedule")
    async def schedule_journey(payload: JourneyScheduleRequest) -> dict[str, Any]:
        steps = tuple(
            JourneyStep(
                code=step.code,
                template=_template(step.template),
                delay=step.delay(),
                exit_on_conversion=step.exit_on_conversion,
            )
            for step in payload.journey.steps
        )
        journey = Journey(
            code=payload.journey.code,
            name=payload.journey.name,
            trigger_event=payload.journey.trigger_event,
            steps=steps,
            status=payload.journey.status,
        )
        scheduled = journey.schedule_for(payload.profile_id, payload.triggered_at)
        return {"count": len(scheduled), "items": scheduled}

    return app


app = create_app()
