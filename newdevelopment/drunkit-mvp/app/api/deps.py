from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db
from app.domain.auth.service import get_consumer_for_token


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
