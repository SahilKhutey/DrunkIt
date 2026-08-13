class RedisKey:

    @staticmethod
    def driver_location(
        driver_id: str,
    ) -> str:

        return (
            f"driver:location:{driver_id}"
        )

    @staticmethod
    def driver_status(
        driver_id: str,
    ) -> str:

        return (
            f"driver:status:{driver_id}"
        )

    @staticmethod
    def idempotency(
        key: str,
    ) -> str:

        return (
            f"idempotency:{key}"
        )

    @staticmethod
    def delivery(
        delivery_id: str,
    ) -> str:

        return (
            f"delivery:{delivery_id}"
        )
