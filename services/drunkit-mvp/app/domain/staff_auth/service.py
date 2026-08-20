"""
Staff authentication (platform admins + retailer staff).

This is the fix for the gap flagged after production hardening: every
/v1/admin/* endpoint used to trust any caller. Now every one requires a
valid StaffSession, and retailer-scoped endpoints additionally enforce
that a RETAILER_STAFF user can only touch their own retailer's data —
see require_retailer_access() in app/api/deps.py, which is where that
enforcement actually happens (this module issues identity, deps.py
enforces scope).

Password hashing uses bcrypt directly — this is a low-volume back-office
login, not worth pulling in a bigger auth framework for.
"""
from __future__ import annotations

import secrets
from datetime import timedelta

import bcrypt
from sqlalchemy.orm import Session as DBSession

from app.core.logging import get_logger
from app.core.time import utcnow
from app.db import models

log = get_logger(__name__)

STAFF_SESSION_TTL_HOURS = 12


class StaffAuthError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # Malformed hash — never let this crash the login attempt into
        # a 500; treat it the same as a wrong password.
        return False


def create_staff_user(
    db: DBSession,
    *,
    email: str,
    password: str,
    role: models.StaffRole,
    retailer_id: str | None = None,
) -> models.StaffUser:
    if role == models.StaffRole.RETAILER_STAFF and retailer_id is None:
        raise StaffAuthError("RETAILER_ID_REQUIRED", "RETAILER_STAFF accounts must have a retailer_id.")
    if role == models.StaffRole.PLATFORM_ADMIN and retailer_id is not None:
        raise StaffAuthError("UNEXPECTED_RETAILER_ID", "PLATFORM_ADMIN accounts must not have a retailer_id.")

    existing = db.query(models.StaffUser).filter_by(email=email).first()
    if existing is not None:
        raise StaffAuthError("EMAIL_ALREADY_REGISTERED", "A staff account with this email already exists.")

    staff = models.StaffUser(
        email=email.strip().lower(),
        password_hash=hash_password(password),
        role=role,
        retailer_id=retailer_id,
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    log.info("staff_user_created", staff_id=staff.id, role=role.value, retailer_id=retailer_id)
    return staff


def login(db: DBSession, *, email: str, password: str) -> models.StaffSession:
    email = email.strip().lower()
    staff = db.query(models.StaffUser).filter_by(email=email).first()

    # Deliberately identical error for "no such user" and "wrong
    # password" — distinguishing them lets an attacker enumerate valid
    # staff emails.
    if staff is None or not staff.active or not _verify_password(password, staff.password_hash):
        log.info("staff_login_failed", email=email)
        raise StaffAuthError("INVALID_CREDENTIALS", "Incorrect email or password.")

    session = models.StaffSession(
        id=secrets.token_hex(32),
        staff_user_id=staff.id,
        expires_at=utcnow() + timedelta(hours=STAFF_SESSION_TTL_HOURS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    log.info("staff_login_success", staff_id=staff.id, role=staff.role.value)
    return session


def get_staff_for_token(db: DBSession, *, token: str) -> models.StaffUser | None:
    session = db.query(models.StaffSession).filter_by(id=token, revoked=False).first()
    if session is None:
        return None
    if session.expires_at < utcnow():
        return None
    if not session.staff_user.active:
        return None
    return session.staff_user
