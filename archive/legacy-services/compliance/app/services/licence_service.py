from datetime import date


class LicenceService:

    async def validate(
        self,
        licence,
    ) -> bool:

        today = date.today()

        if licence.status != "ACTIVE":
            return False

        if licence.valid_from > today:
            return False

        if licence.valid_until < today:
            return False

        return True
