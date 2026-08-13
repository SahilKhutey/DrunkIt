from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.driver.enums import (
    DriverAccountStatus,
    DriverOperationalStatus,
    VerificationStatus,
)
from app.domain.driver.models import Driver


class DriverRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        driver: Driver,
    ) -> Driver:

        self.session.add(driver)

        await self.session.flush()

        await self.session.refresh(driver)

        return driver

    async def get_by_id(
        self,
        driver_id: str,
    ) -> Driver | None:

        result = await self.session.execute(
            select(Driver).where(
                Driver.id == driver_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: str,
    ) -> Driver | None:

        result = await self.session.execute(
            select(Driver).where(
                Driver.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_available_drivers(
        self,
    ) -> list[Driver]:

        result = await self.session.execute(
            select(Driver).where(
                Driver.account_status == DriverAccountStatus.ACTIVE,
                Driver.operational_status == DriverOperationalStatus.AVAILABLE,
                Driver.verification_status == VerificationStatus.VERIFIED,
            )
        )

        return list(result.scalars().all())
