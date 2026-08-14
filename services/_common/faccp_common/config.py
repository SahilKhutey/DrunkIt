"""Production configuration validation and guardrails."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "local"
    database_url: str = "postgresql+asyncpg://drunkit:drunkit_dev@localhost:5432/drunkit"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    jwt_issuer: str = "drunkit-platform"
    jwt_audience: str = "drunkit-api"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


# Backward compatibility alias for microservices using BaseServiceSettings
BaseServiceSettings = Settings


def validate_production_config(settings: Settings) -> None:
    """Ensure production configuration contains no development placeholders or defaults."""
    if settings.environment != "production":
        return

    forbidden = ("CHANGE_ME", "password", "secret", "localhost", "127.0.0.1", "dev-password")
    values = [
        settings.database_url,
        settings.redis_url,
        settings.jwt_issuer,
        settings.jwt_audience,
    ]

    for val in values:
        if any(marker in val.lower() for marker in forbidden):
            raise RuntimeError(f"Unsafe production configuration detected: {val}")


def reject_dev_configuration(environment: str, values: dict[str, str]) -> None:
    """Reject dev passwords, localhost URIs, and placeholder tokens in production environment."""
    if environment != "production":
        return

    for key, value in values.items():
        lowered = value.lower()
        if "localhost" in lowered or "127.0.0.1" in lowered:
            raise RuntimeError(f"Production configuration key '{key}' points to localhost")
        if "change_me" in lowered or "dev-password" in lowered or "secret" in lowered:
            raise RuntimeError(f"Production configuration key '{key}' contains placeholder or default secret")
