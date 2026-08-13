from sqlalchemy import select, update
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

    async def reserve_driver(
        self,
        driver_id: str,
    ) -> bool:

        result = await self.session.execute(
            update(Driver)
            .where(
                Driver.id == driver_id,
                Driver.account_status == DriverAccountStatus.ACTIVE,
                Driver.verification_status == VerificationStatus.VERIFIED,
                Driver.operational_status == DriverOperationalStatus.AVAILABLE,
            )
            .values(operational_status=DriverOperationalStatus.RESERVED)
        )

        await self.session.commit()

        return result.rowcount == 1

    async def release_driver(
        self,
        driver_id: str,
    ) -> bool:

        result = await self.session.execute(
            update(Driver)
            .where(
                Driver.id == driver_id,
                Driver.operational_status == DriverOperationalStatus.RESERVED,
            )
            .values(operational_status=DriverOperationalStatus.AVAILABLE)
        )

        await self.session.commit()

        return result.rowcount == 1

