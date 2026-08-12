"""Realtime service configuration."""

from __future__ import annotations

from faccp_common.config import BaseServiceSettings


class RealtimeServiceSettings(BaseServiceSettings):
    service_name: str = "faccp-realtime"
    port: int = 8012


_settings: RealtimeServiceSettings | None = None


def get_settings() -> RealtimeServiceSettings:
    global _settings
    if _settings is None:
        _settings = RealtimeServiceSettings()
    return _settings
