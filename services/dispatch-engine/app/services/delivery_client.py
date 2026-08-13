import httpx

from app.core.config import settings


class DeliveryServiceClient:

    async def move_to_dispatching(
        self,
        delivery_id: str,
    ):

        url = (
            f"{settings.delivery_service_url}"
            f"/deliveries/{delivery_id}/transition"
        )

        payload = {
            "target_status": "DISPATCHING",
        }

        async with httpx.AsyncClient(
            timeout=5.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

            return response.json()

    async def assign_driver(
        self,
        delivery_id: str,
        driver_id: str,
    ):

        url = (
            f"{settings.delivery_service_url}"
            f"/deliveries/{delivery_id}"
            "/assign-driver"
        )

        payload = {
            "driver_id": driver_id,
        }

        async with httpx.AsyncClient(
            timeout=5.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

            return response.json()

    async def move_to_assigned(
        self,
        delivery_id: str,
    ):

        url = (
            f"{settings.delivery_service_url}"
            f"/deliveries/{delivery_id}/transition"
        )

        payload = {
            "target_status": "ASSIGNED",
        }

        async with httpx.AsyncClient(
            timeout=5.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

            return response.json()
