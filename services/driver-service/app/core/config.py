from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    app_name: str = "Driver Service"

    environment: str = "development"

    database_url: str = (
        "postgresql+asyncpg://"
        "driver:driver@localhost:5433/driver"
    )

    redis_url: str = (
        "redis://localhost:6379/2"
    )

    api_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
