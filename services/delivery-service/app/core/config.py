from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Delivery Engine"
    environment: str = "development"

    database_url: str = (
        "postgresql+asyncpg://delivery:delivery@localhost:5432/delivery"
    )

    api_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
