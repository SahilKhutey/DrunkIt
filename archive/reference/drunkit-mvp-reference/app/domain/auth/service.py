"""
Phone + OTP authentication.

This is the identity boundary for the whole consumer API: every
consumer-scoped endpoint trusts the Session this module issues, never
a client-supplied consumer_id. That's the fix this module exists to
make — passing your own consumer_id used to be enough to act as
anyone.

DEV-MODE NOTE: there is no real SMS provider wired in. request_otp()
returns the raw code directly in the response when environment !=
"production" so the flow is testable end-to-end without SMS. Before
any real launch, swap the "return the code" branch for a call to an
actual SMS provider (MSG91, Twilio, etc.) and delete that branch
entirely — the seam is deliberately isolated in one place below.

ABUSE NOTE: an IP-based rate limit (see core/limiter.py) covers "one
IP hitting us too fast," but does nothing to stop someone spraying OTP
requests at one victim's phone number from many different IPs/devices
— every request costs the platform real SMS spend and harasses that
person's phone. OTP_REQUEST_COOLDOWN_SECONDS below is the IP-independent
defense: it throttles by phone number itself, at the data layer.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from sqlalchemy.orm import Session as DBSession

from app.core.config import get_settings
from app.core.logging import get_logger, mask_phone
from app.core.time import utcnow
from app.db import models

settings = get_settings()
log = get_logger(__name__)

OTP_TTL_SECONDS = 5 * 60
OTP_MAX_ATTEMPTS = 5
OTP_REQUEST_COOLDOWN_SECONDS = 45
SESSION_TTL_DAYS = 30


class AuthError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def _hash_code(code: str) -> str:
    # Codes are short-lived (5 min) and single-use; a fast hash is fine
    # here, this is not a password store.
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def request_otp(db: DBSession, *, phone: str) -> tuple[str, int, str | None]:
    """
    Returns (request_id, expires_in_seconds, dev_otp).
    dev_otp is None outside development — see module docstring.
    """
    phone = phone.strip()

    most_recent = (
        db.query(models.OTPChallenge)
        .filter_by(phone=phone)
        .order_by(models.OTPChallenge.created_at.desc())
        .first()
    )
    if most_recent is not None:
        seconds_since = (utcnow() - most_recent.created_at).total_seconds()
        if seconds_since < OTP_REQUEST_COOLDOWN_SECONDS:
            wait = int(OTP_REQUEST_COOLDOWN_SECONDS - seconds_since)
            log.info("otp_request_cooldown_blocked", phone=mask_phone(phone), wait_seconds=wait)
            raise AuthError(
                "COOLDOWN_ACTIVE",
                f"Please wait {wait}s before requesting another code.",
            )

    consumer = db.query(models.Consumer).filter_by(phone=phone).first()
    if consumer is None:
        consumer = models.Consumer(phone=phone)
        db.add(consumer)
        db.flush()

    code = _generate_code()
    challenge = models.OTPChallenge(
        phone=phone,
        code_hash=_hash_code(code),
        expires_at=utcnow() + timedelta(seconds=OTP_TTL_SECONDS),
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    log.info("otp_requested", phone=mask_phone(phone), challenge_id=challenge.id)

    dev_otp = code if settings.environment != "production" else None
    return challenge.id, OTP_TTL_SECONDS, dev_otp


def verify_otp(db: DBSession, *, phone: str, code: str) -> models.Session:
    phone = phone.strip()

    challenge = (
        db.query(models.OTPChallenge)
        .filter_by(phone=phone, consumed=False)
        .order_by(models.OTPChallenge.created_at.desc())
        .first()
    )
    if challenge is None:
        log.info("otp_verify_no_active_challenge", phone=mask_phone(phone))
        raise AuthError("NO_ACTIVE_CHALLENGE", "No active verification code for this number. Request a new one.")

    if challenge.expires_at < utcnow():
        log.info("otp_verify_expired", phone=mask_phone(phone))
        raise AuthError("CODE_EXPIRED", "Verification code has expired. Request a new one.")

    if challenge.attempts >= OTP_MAX_ATTEMPTS:
        log.warning("otp_verify_locked_out", phone=mask_phone(phone))
        raise AuthError("TOO_MANY_ATTEMPTS", "Too many incorrect attempts. Request a new code.")

    if challenge.code_hash != _hash_code(code.strip()):
        challenge.attempts += 1
        db.add(challenge)
        db.commit()
        log.info("otp_verify_wrong_code", phone=mask_phone(phone), attempts=challenge.attempts)
        raise AuthError("INVALID_CODE", "Incorrect verification code.")

    challenge.consumed = True
    db.add(challenge)

    consumer = db.query(models.Consumer).filter_by(phone=phone).first()
    if consumer is None:
        # Shouldn't happen — request_otp always creates the consumer —
        # but fail loudly rather than silently creating a duplicate.
        raise AuthError("CONSUMER_NOT_FOUND", "No consumer record for this number.")

    session = models.Session(
        id=secrets.token_hex(32),
        consumer_id=consumer.id,
        expires_at=utcnow() + timedelta(days=SESSION_TTL_DAYS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    log.info("otp_verified_session_issued", phone=mask_phone(phone), consumer_id=consumer.id)
    return session


def get_consumer_for_token(db: DBSession, *, token: str) -> models.Consumer | None:
    session = db.query(models.Session).filter_by(id=token, revoked=False).first()
    if session is None:
        return None
    if session.expires_at < utcnow():
        return None
    return session.consumer
