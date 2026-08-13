import httpx

from app.core.config import settings
from app.schemas.dispatch import DriverCandidate


class DriverServiceClient:

    async def get_available_drivers(
        self,
    ) -> list[DriverCandidate]:

        url = (
            f"{settings.driver_service_url}"
            "/internal/drivers/available"
        )

        async with httpx.AsyncClient(
            timeout=5.0
        ) as client:

            response = await client.get(url)

            response.raise_for_status()

            data = response.json()

        return [
            DriverCandidate(**driver)
            for driver in data["drivers"]
        ]

    async def reserve_driver(
        self,
        driver_id: str,
        delivery_id: str,
    ) -> bool:

        url = (
            f"{settings.driver_service_url}"
            f"/internal/drivers/{driver_id}/reserve"
        )

        payload = {
            "delivery_id": delivery_id,
        }

        async with httpx.AsyncClient(
            timeout=5.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

        if response.status_code == 409:
            return False

        response.raise_for_status()

        return True
