from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from app.domain.cdp import CDPEvent, ConsentLedger, IdentityGraph, SegmentEngine
from app.schemas import AudienceRequest, ConsentRequest, EventRequest, ResolveProfileRequest


class CDPState:
    def __init__(self) -> None:
        self.identity_graph = IdentityGraph()
        self.consent = ConsentLedger()
        self.segments = SegmentEngine()


def _profile_payload(profile: Any, segments: set[str] | None = None) -> dict[str, Any]:
    return {
        "profile_id": profile.profile_id,
        "identifiers": {key: sorted(values) for key, values in profile.identifiers.items()},
        "traits": profile.traits,
        "order_count": profile.order_count,
        "lifetime_value": str(profile.lifetime_value),
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
        "segments": sorted(segments or []),
    }


def create_app() -> FastAPI:
    app = FastAPI(title="FACCP CDP Service", version="0.1.0")
    state = CDPState()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "faccp-cdp"}

    @app.post("/api/v1/cdp/profiles/resolve", status_code=201)
    async def resolve_profile(payload: ResolveProfileRequest) -> dict[str, Any]:
        profile = state.identity_graph.resolve(payload.identifiers, payload.traits)
        segments = state.segments.assign(profile)
        return {"data": _profile_payload(profile, segments)}

    @app.post("/api/v1/cdp/events", status_code=202)
    async def record_event(payload: EventRequest) -> dict[str, str]:
        try:
            profile = state.identity_graph.get(payload.profile_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        profile.record(
            CDPEvent(
                profile_id=payload.profile_id,
                event_type=payload.event_type,
                occurred_at=payload.occurred_at,
                properties=payload.properties,
                value=payload.value,
            )
        )
        return {"status": "accepted"}

    @app.post("/api/v1/cdp/consent/grants", status_code=202)
    async def grant_consent(payload: ConsentRequest) -> dict[str, str]:
        state.consent.grant(payload.profile_id, set(payload.scopes))
        return {"status": "accepted"}

    @app.post("/api/v1/cdp/consent/revocations", status_code=202)
    async def revoke_consent(payload: ConsentRequest) -> dict[str, str]:
        state.consent.revoke(payload.profile_id, set(payload.scopes))
        return {"status": "accepted"}

    @app.post("/api/v1/cdp/audiences")
    async def build_audience(payload: AudienceRequest) -> dict[str, Any]:
        audience = state.segments.build_audience(
            state.identity_graph.all_profiles(),
            payload.segment,
            state.consent,
            payload.consent_scope,
            payload.now,
        )
        return {"segment": payload.segment, "count": len(audience), "items": audience}

    return app


app = create_app()
