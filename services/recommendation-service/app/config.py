"""Recommendation service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class RecommendationServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-recommendation"
    port: int = 8014
    database_url: str = "postgresql+asyncpg://faccp:faccp_dev_password_change_in_production@localhost:5432/faccp_recommendation"


_settings: RecommendationServiceSettings | None = None


def get_settings() -> RecommendationServiceSettings:
    global _settings
    if _settings is None:
        _settings = RecommendationServiceSettings()
    return _settings
