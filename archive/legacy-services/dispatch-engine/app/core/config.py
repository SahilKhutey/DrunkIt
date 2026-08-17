from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Dispatch Engine"

    environment: str = "development"

    driver_service_url: str = (
        "http://localhost:8001/api/v1"
    )

    delivery_service_url: str = (
        "http://localhost:8000/api/v1"
    )

    candidate_limit: int = 20

    max_driver_distance_km: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
