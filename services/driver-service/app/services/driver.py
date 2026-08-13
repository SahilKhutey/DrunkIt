from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.driver.enums import (
    DriverAccountStatus,
    DriverOperationalStatus,
    VerificationStatus,
)

from app.domain.driver.models import Driver

from app.domain.driver.state_machine import (
    validate_transition,
)

from app.repositories.driver import DriverRepository

from app.schemas.driver import (
    DriverCreate,
)


class DriverService:

    def __init__(
        self,
        session: AsyncSession,
    ):

        self.session = session

        self.repository = DriverRepository(
            session
        )

    async def create_driver(
        self,
        data: DriverCreate,
    ) -> Driver:

        existing = await self.repository.get_by_user_id(
            data.user_id
        )

        if existing:

            raise ValueError(
                "Driver already exists"
            )

        driver = Driver(

            user_id=data.user_id,

            name=data.name,

            phone=data.phone,

            vehicle_type=data.vehicle_type,

            account_status=(
                DriverAccountStatus.PENDING
            ),

            operational_status=(
                DriverOperationalStatus.OFFLINE
            ),

            verification_status=(
                VerificationStatus.PENDING
            ),
        )

        await self.repository.create(
            driver
        )

        await self.session.commit()

        return driver

    async def change_status(
        self,
        driver: Driver,
        target: DriverOperationalStatus,
    ) -> Driver:

        if (
            driver.account_status
            != DriverAccountStatus.ACTIVE
        ):

            raise ValueError(
                "Driver account is not active"
            )

        if (
            driver.verification_status
            != VerificationStatus.VERIFIED
        ):

            raise ValueError(
                "Driver is not verified"
            )

        validate_transition(
            driver.operational_status,
            target,
        )

        driver.operational_status = target

        await self.session.commit()

        await self.session.refresh(
            driver
        )

        return driver
