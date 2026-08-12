"""
Consent Management Policy as codified in Article 2 of the System Constitution (§2.3).
"""

from __future__ import annotations


class ConsentPolicy:
    REQUIRED_CONSENTS: dict[str, str] = {
        "marketing": "Send promotional communications",
        "analytics": "Analyze usage to improve service",
        "profiling": "Build personal profile for personalization",
        "third_party_sharing": "Share with partner retailers",
        "location_tracking": "Track precise location for delivery",
    }

    CONSENT_DEFAULT_VALUES: dict[str, bool] = {
        "marketing": False,        # Explicit Opt-in required
        "analytics": True,         # Opt-out allowed (legitimate interest)
        "profiling": False,        # Explicit Opt-in required
        "third_party_sharing": False,  # Explicit Opt-in required
        "location_tracking": True, # Required for core delivery service
    }

    CONSENT_RETENTION_DAYS = 365 * 7  # 7 years for legal compliance audit
