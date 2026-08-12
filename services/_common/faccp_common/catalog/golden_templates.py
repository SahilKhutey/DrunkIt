"""
Golden Templates Registry (Architectural Core Templates).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass
class GoldenTemplate:
    name: str
    purpose: str
    owner_domain: str
    requires_arch_review: bool = True


class GoldenTemplateRegistry:
    TEMPLATES: ClassVar[dict[str, GoldenTemplate]] = {
        "secure-api": GoldenTemplate("Secure API (Golden)", "Standard OpenAPI Endpoint with Auth/ABAC", "Trust"),
        "secure-service": GoldenTemplate("Secure Service (Golden)", "FastAPI Microservice with Security Middleware", "Platform"),
        "compliance-service": GoldenTemplate("Compliance Service (Golden)", "Policy Evaluation Engine Microservice", "Compliance"),
        "payment-service": GoldenTemplate("Payment Service (Golden)", "Idempotent Double-Entry Payment Service", "Finance"),
        "identity-service": GoldenTemplate("Identity Service (Golden)", "Vault-backed Identity & KYC Service", "Trust"),
        "audit-service": GoldenTemplate("Audit Service (Golden)", "Append-only Immutable Audit Log Service", "Audit"),
        "integration-service": GoldenTemplate("Integration Service (Golden)", "Vendor-agnostic External Integration Adapter", "Platform"),
    }

    @classmethod
    def get_template(cls, template_id: str) -> GoldenTemplate:
        if template_id not in cls.TEMPLATES:
            raise KeyError(f"Golden template '{template_id}' not found")
        return cls.TEMPLATES[template_id]
