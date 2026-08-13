from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.driver.models import Driver

from app.schemas.driver import (
    DriverLocationUpdate,
)


class LocationService:

    def __init__(
        self,
        session: AsyncSession,
    ):

        self.session = session

    async def update_location(
        self,
        driver: Driver,
        data: DriverLocationUpdate,
    ) -> Driver:

        if not driver.is_location_enabled:

            raise ValueError(
                "Location tracking is disabled"
            )

        driver.latitude = data.latitude

        driver.longitude = data.longitude

        driver.location_updated_at = (
            datetime.now(timezone.utc)
        )

        await self.session.commit()

        await self.session.refresh(
            driver
        )

        return driver
