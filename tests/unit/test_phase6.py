from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.domain.cdp import CDPEvent, ConsentLedger, IdentityGraph, SegmentEngine
from app.main import create_app


def test_identity_graph_resolves_and_merges_profiles_across_identifiers():
    graph = IdentityGraph()
    by_email = graph.resolve({"email": "Buyer@Example.com"}, {"state": "IN-KA"})
    by_phone = graph.resolve({"phone": "+919876543210"}, {"language": "en"})

    merged = graph.resolve({"email": "buyer@example.com", "phone": "+919876543210"})

    assert merged.profile_id == by_email.profile_id
    assert len(graph.all_profiles()) == 1
    assert merged.identifiers["email"] == {"buyer@example.com"}
    assert merged.identifiers["phone"] == {"+919876543210"}
    assert merged.traits["state"] == "IN-KA"
    assert by_phone.profile_id not in {profile.profile_id for profile in graph.all_profiles() if profile is not merged}


def test_segment_engine_assigns_rfm_segments():
    now = datetime.now(timezone.utc)
    profile = IdentityGraph().resolve({"consumer_id": "cons_1"}, {"uses_promotions": True})
    for days_ago, amount in [(3, "6000"), (8, "7000"), (12, "5000"), (18, "4000"), (25, "5000")]:
        profile.record(
            CDPEvent(
                profile_id=profile.profile_id,
                event_type="order.completed",
                occurred_at=now - timedelta(days=days_ago),
                value=Decimal(amount),
            )
        )

    segments = SegmentEngine(high_value_threshold=Decimal("25000")).assign(profile, now)

    assert {"high_value", "loyal", "discount_sensitive"} <= segments


def test_consent_ledger_filters_audience_exports():
    graph = IdentityGraph()
    opted_in = graph.resolve({"email": "in@example.com"})
    opted_out = graph.resolve({"email": "out@example.com"})
    consent = ConsentLedger()
    consent.grant(opted_in.profile_id, {"marketing"})

    audience = SegmentEngine().build_audience(
        [opted_in, opted_out],
        "new_customer",
        consent,
        scope="marketing",
    )

    assert [row["profile_id"] for row in audience] == [opted_in.profile_id]


def test_cdp_app_exposes_phase6_routes():
    app = create_app()
    paths = {route.path for route in app.routes}

    assert "/api/v1/cdp/profiles/resolve" in paths
    assert "/api/v1/cdp/events" in paths
    assert "/api/v1/cdp/consent/grants" in paths
    assert "/api/v1/cdp/audiences" in paths
