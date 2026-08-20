from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db
from app.domain.auth.service import get_consumer_for_token
from app.domain.staff_auth.service import get_staff_for_token


def _extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


def get_current_consumer(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> models.Consumer:
    """
    Required auth. Use on any endpoint that changes state or reveals
    another consumer's data (eligibility verification, orders,
    delivery tracking). Raises 401 rather than falling back to any
    client-supplied identifier.
    """
    token = _extract_token(authorization)
    if token is None:
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")

    consumer = get_consumer_for_token(db, token=token)
    if consumer is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    return consumer


def get_optional_consumer(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> models.Consumer | None:
    """
    Optional auth. Use on endpoints that should work for anonymous
    browsing (e.g. listings) but personalize when a valid session is
    present. Never raises — an invalid/missing token just means
    "anonymous," which for a browsing endpoint is a normal case, not
    an error.
    """
    token = _extract_token(authorization)
    if token is None:
        return None
    return get_consumer_for_token(db, token=token)


# ---------------------------------------------------------------------------
# Staff auth (admin/retailer). A consumer bearer token is issued from a
# completely different table (Session vs StaffSession) — there is no
# code path where a consumer's token accidentally satisfies a staff
# dependency, or vice versa.
# ---------------------------------------------------------------------------

def get_current_staff(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> models.StaffUser:
    """
    Required for every /v1/admin/* endpoint. Identifies WHO is calling
    but does not by itself authorize WHAT they can touch — see
    require_retailer_access() below for resource-level scoping.
    """
    token = _extract_token(authorization)
    if token is None:
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")

    staff = get_staff_for_token(db, token=token)
    if staff is None:
        raise HTTPException(status_code=401, detail="Invalid or expired staff session.")

    return staff


def require_platform_admin(
    staff: models.StaffUser = Depends(get_current_staff),
) -> models.StaffUser:
    """
    Use on endpoints that only a platform admin may call regardless of
    retailer — retailer creation/verification, product catalog
    changes, and delivery/driver ops (dispatch is a platform-run
    resource, not something individual retailers control in this
    architecture).
    """
    if staff.role != models.StaffRole.PLATFORM_ADMIN:
        raise HTTPException(status_code=403, detail="This action requires a platform admin account.")
    return staff


def check_retailer_access(staff: models.StaffUser, retailer_id: str) -> None:
    """
    Authorizes access to a SPECIFIC retailer's resources: a
    PLATFORM_ADMIN may access any retailer; a RETAILER_STAFF user may
    only access their own retailer_id. Called explicitly inside an
    endpoint body — after the request payload has been parsed and the
    target retailer_id is known — rather than as a Depends() default,
    since a dependency's defaults are fixed at function-definition
    time and can't reference another parameter's runtime value.
    """
    if staff.role == models.StaffRole.PLATFORM_ADMIN:
        return
    if staff.role == models.StaffRole.RETAILER_STAFF and staff.retailer_id == retailer_id:
        return
    raise HTTPException(status_code=403, detail="You don't have access to this retailer's resources.")
