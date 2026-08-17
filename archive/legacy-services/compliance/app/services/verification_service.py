from datetime import datetime, timezone


class VerificationService:

    async def is_valid(
        self,
        verification,
    ) -> bool:

        now = datetime.now(timezone.utc)

        if verification.status != "VERIFIED":
            return False

        if verification.revoked_at:
            return False

        if (
            verification.expires_at
            and verification.expires_at <= now
        ):
            return False

        return True


def is_fresh(
    verified_at: datetime | None,
    max_age_seconds: int,
) -> bool:

    if verified_at is None:
        return False

    now = datetime.now(timezone.utc)

    # Handle naive / timezone aware datetimes
    if verified_at.tzinfo is None:
        verified_at = verified_at.replace(tzinfo=timezone.utc)

    age = (now - verified_at).total_seconds()
    return age <= max_age_seconds
