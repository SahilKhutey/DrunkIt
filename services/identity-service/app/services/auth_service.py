"""Authentication service: registration, login, MFA, session management, password flows."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pyotp
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.communication.request_envelope import CorrelationContext
from faccp_common.exceptions import (
    BadRequestError, ConflictError, NotFoundError, UnauthorizedError,
)
from faccp_common.logging import get_logger
from faccp_common.security import FieldEncryption
from faccp_common.trust.authentication import (
    TokenValidator, create_access_token, create_refresh_token,
    generate_otp, hash_password, hash_token, verify_password,
)
from faccp_common.trust.identity import ActorType, AuthenticatedContext, Identity

from app.config import get_settings
from app.db.models import (
    APIKey, Device, EmailVerificationToken, PasswordResetToken, Session, User,
)
from app.schemas.auth import (
    LoginRequest, MFASetupResponse, MFAVerifyRequest, PasswordChangeRequest,
    PasswordResetConfirm, PasswordResetRequest, RegisterRequest, TokenResponse,
)

logger = get_logger(__name__)
settings = get_settings()
_encryption = FieldEncryption(settings.field_encryption_key)


class MFARequiredError(UnauthorizedError):
    code = "MFA_REQUIRED"
    default_message = "MFA code required"


class SecurityError(UnauthorizedError):
    code = "SECURITY_ERROR"
    default_message = "Security violation."


class AuthService:
    """End-to-end authentication and identity management."""

    def __init__(
        self, db: AsyncSession, producer: EventProducer | None = None,
    ) -> None:
        self.db = db
        self.producer = producer
        self._validator = TokenValidator(settings.jwt_secret)

    # ============================================================
    # REGISTRATION
    # ============================================================
    async def register(
        self, payload: RegisterRequest, *, ip_address: str, user_agent: str,
        device_fingerprint: str | None = None, device_name: str | None = None,
    ) -> TokenResponse:
        existing = await self._get_user_by_email(payload.email)
        if existing:
            raise ConflictError("Email already registered", details={"field": "email"})

        user = User(
            id=Identity.new_id(),
            email=payload.email.lower(),
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            primary_role=payload.primary_role,
            roles=[payload.primary_role],
            locale=payload.locale,
            timezone=payload.timezone,
            consumer_level="C1_REGISTERED" if payload.primary_role == "CONSUMER" else None,
            seller_level="S0_APPLICATION" if payload.primary_role == "RETAILER_OWNER" else None,
        )
        self.db.add(user)

        # Register device if provided
        device = None
        fingerprint = payload.device_fingerprint or device_fingerprint
        if fingerprint:
            device = Device(
                user_id=user.id, device_fingerprint=fingerprint,
                device_name=payload.device_name or device_name or "Unknown device", last_ip=ip_address,
                is_trusted=True,  # first device auto-trusted
            )
            self.db.add(device)

        # Email verification token
        email_token = EmailVerificationToken(
            user_id=user.id, token_hash=hash_token(secrets.token_urlsafe(32)),
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        self.db.add(email_token)
        await self.db.commit()
        await self.db.refresh(user)

        await self._publish("identity.registered", {
            "user_id": user.id, "email": user.email, "role": user.primary_role,
        })
        return await self._issue_tokens(user, ip_address, user_agent, device, mfa_verified=False)

    # ============================================================
    # LOGIN
    # ============================================================
    async def login(
        self, payload: LoginRequest, *, ip_address: str, user_agent: str,
    ) -> TokenResponse:
        user = await self._get_user_by_email(payload.email)
        if user is None:
            verify_password(payload.password, "$argon2id$v=19$m=65536,t=3,p=4$" + "x" * 22 + "$" + "x" * 43)
            raise UnauthorizedError("Invalid credentials")

        # Check lockout
        if user.is_locked and user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise UnauthorizedError(
                f"Account locked until {user.locked_until.isoformat()}",
                details={"locked_until": user.locked_until.isoformat()},
            )
        if user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0
            user.locked_until = None

        # Verify password
        if not verify_password(payload.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.max_login_attempts:
                user.is_locked = True
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.login_lockout_minutes)
                await self._publish("identity.locked", {
                    "user_id": user.id, "reason": "too_many_failed_attempts",
                    "locked_until": user.locked_until.isoformat(),
                })
            await self.db.commit()
            raise UnauthorizedError("Invalid credentials")

        if not user.is_active:
            raise UnauthorizedError("Account is not active")

        mfa_verified = False
        if user.mfa_enabled:
            if not payload.mfa_code:
                await self.db.commit()
                raise MFARequiredError("MFA code required", details={"mfa_method": user.mfa_method})
            if not self._verify_totp(user, payload.mfa_code):
                await self.db.commit()
                raise UnauthorizedError("Invalid MFA code")
            mfa_verified = True

        # Register/update device
        device = None
        if payload.device_fingerprint:
            device = await self._upsert_device(user, payload.device_fingerprint,
                                               payload.device_name, ip_address)

        # Update login metadata
        user.last_login_at = datetime.now(timezone.utc)
        user.last_login_ip = ip_address
        user.failed_login_attempts = 0
        await self.db.commit()
        await self.db.refresh(user)

        await self._enforce_session_limit(user.id)

        await self._publish("identity.login", {
            "user_id": user.id, "ip": ip_address, "device_id": device.id if device else None,
        })
        return await self._issue_tokens(user, ip_address, user_agent, device, mfa_verified=mfa_verified)

    # ============================================================
    # TOKEN REFRESH (with rotation + reuse detection)
    # ============================================================
    async def refresh_tokens(
        self, refresh_token: str, *, ip_address: str, user_agent: str,
    ) -> TokenResponse:
        result = self._validator.validate_refresh_token(refresh_token)
        if not result.valid:
            raise UnauthorizedError(result.error or "Invalid refresh token")

        claims = result.claims
        user_id = claims["sub"]
        token_hash = hash_token(refresh_token)
        family_id = claims.get("token_family_id", "")

        # Find session
        session_result = await self.db.execute(
            select(Session).where(
                Session.refresh_token_hash == token_hash,
                Session.user_id == user_id,
                Session.is_active == True,  # noqa: E712
            )
        )
        session = session_result.scalar_one_or_none()
        if not session:
            raise UnauthorizedError("Session not found or revoked")

        # Reuse detection — REPLAY ATTACK
        if not session.is_active:
            await self._publish("identity.refresh_reuse_detected", {
                "user_id": user_id, "session_id": session.id, "family_id": family_id,
            }, severity="critical")
            await self._revoke_token_family(family_id, "refresh_reuse_detected")
            raise SecurityError("Refresh token reuse detected. All sessions revoked.")

        # Rotate
        session.is_active = False
        session.revoked_at = datetime.now(timezone.utc)
        session.revoked_reason = "rotated"

        user = await self._get_user_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not active")

        await self.db.commit()
        return await self._issue_tokens(user, ip_address, user_agent, mfa_verified=True)

    async def _revoke_token_family(self, family_id: str, reason: str) -> None:
        await self.db.execute(
            update(Session)
            .where(Session.token_family_id == family_id, Session.is_active == True)  # noqa: E712
            .values(is_active=False, revoked_at=datetime.now(timezone.utc), revoked_reason=reason)
        )
        await self.db.commit()

    # ============================================================
    # LOGOUT
    # ============================================================
    async def logout(self, user_id: str, refresh_token: str | None = None, all_devices: bool = False) -> None:
        if all_devices:
            await self.db.execute(
                update(Session)
                .where(Session.user_id == user_id, Session.is_active == True)  # noqa: E712
                .values(is_active=False, revoked_at=datetime.now(timezone.utc), revoked_reason="logout_all")
            )
        elif refresh_token:
            token_hash = hash_token(refresh_token)
            await self.db.execute(
                update(Session)
                .where(
                    Session.user_id == user_id, Session.refresh_token_hash == token_hash,
                    Session.is_active == True,  # noqa: E712
                )
                .values(is_active=False, revoked_at=datetime.now(timezone.utc), revoked_reason="logout")
            )
        else:
            raise BadRequestError("Provide refresh_token or set all_devices=true")
        await self.db.commit()
        await self._publish("identity.logout", {"user_id": user_id, "all_devices": all_devices})

    # ============================================================
    # PASSWORD MANAGEMENT
    # ============================================================
    async def change_password(self, user_id: str, payload: PasswordChangeRequest) -> None:
        user = await self._get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if not verify_password(payload.current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")

        user.password_hash = hash_password(payload.new_password)
        # Revoke all other sessions
        await self.db.execute(
            update(Session)
            .where(Session.user_id == user_id, Session.is_active == True)  # noqa: E712
            .values(is_active=False, revoked_at=datetime.now(timezone.utc), revoked_reason="password_changed")
        )
        await self.db.commit()
        await self._publish("identity.password_changed", {"user_id": user_id})

    async def request_password_reset(self, payload: PasswordResetRequest) -> None:
        user = await self._get_user_by_email(payload.email)
        if user is None:
            return  # don't reveal
        token = secrets.token_urlsafe(32)
        reset = PasswordResetToken(
            user_id=user.id, token_hash=hash_token(token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        self.db.add(reset)
        await self.db.commit()
        await self._publish("identity.password_reset_requested", {
            "user_id": user.id, "email": user.email,
        })

    async def confirm_password_reset(self, payload: PasswordResetConfirm) -> None:
        token_hash = hash_token(payload.token)
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
            )
        )
        reset = result.scalar_one_or_none()
        if not reset or reset.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedError("Invalid or expired token")

        user = await self._get_user_by_id(reset.user_id)
        if not user:
            raise NotFoundError("User not found")
        user.password_hash = hash_password(payload.new_password)
        reset.used_at = datetime.now(timezone.utc)
        await self.db.execute(
            update(Session)
            .where(Session.user_id == user.id, Session.is_active == True)  # noqa: E712
            .values(is_active=False, revoked_at=datetime.now(timezone.utc), revoked_reason="password_reset")
        )
        await self.db.commit()
        await self._publish("identity.password_reset_completed", {"user_id": user.id})

    # ============================================================
    # MFA
    # ============================================================
    async def setup_mfa(self, user_id: str) -> MFASetupResponse:
        user = await self._get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if user.mfa_enabled:
            raise ConflictError("MFA already enabled")

        secret = pyotp.random_base32()
        user.mfa_secret_encrypted = _encryption.encrypt(secret)
        backup_codes = [generate_otp(8) for _ in range(10)]
        user.mfa_backup_codes_hashed = [hash_token(c) for c in backup_codes]
        await self.db.commit()

        otpauth_url = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="FACCP")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?data={otpauth_url}&size=200x200"
        return MFASetupResponse(secret=secret, qr_code_url=qr_url, backup_codes=backup_codes)

    async def verify_mfa_setup(self, user_id: str, payload: MFAVerifyRequest) -> bool:
        user = await self._get_user_by_id(user_id)
        if not user or not user.mfa_secret_encrypted:
            raise NotFoundError("MFA setup not initiated")
        if user.mfa_enabled:
            raise ConflictError("MFA already enabled")

        secret = _encryption.decrypt(user.mfa_secret_encrypted)
        if pyotp.TOTP(secret).verify(payload.code, valid_window=1):
            user.mfa_enabled = True
            user.mfa_method = "TOTP"
            user.mfa_enrolled_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self._publish("identity.mfa_enabled", {"user_id": user_id})
            return True
        return False

    async def disable_mfa(self, user_id: str, current_password: str) -> None:
        user = await self._get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if not verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")
        if not user.mfa_enabled:
            raise ConflictError("MFA not enabled")
        user.mfa_enabled = False
        user.mfa_method = None
        user.mfa_secret_encrypted = None
        user.mfa_backup_codes_hashed = []
        user.mfa_enrolled_at = None
        await self.db.commit()
        await self._publish("identity.mfa_disabled", {"user_id": user_id})

    # ============================================================
    # PROFILE
    # ============================================================
    async def get_profile(self, user_id: str) -> User:
        user = await self._get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def list_sessions(self, user_id: str) -> list[Session]:
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id, Session.is_active == True)  # noqa: E712
            .order_by(Session.last_used_at.desc())
        )
        return list(result.scalars().all())

    # ============================================================
    # HELPERS
    # ============================================================
    async def _get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def _upsert_device(
        self, user: User, fingerprint: str, name: str | None, ip: str
    ) -> Device:
        result = await self.db.execute(
            select(Device).where(
                Device.user_id == user.id, Device.device_fingerprint == fingerprint
            )
        )
        device = result.scalar_one_or_none()
        if device is None:
            device = Device(
                user_id=user.id, device_fingerprint=fingerprint,
                device_name=name or "Unknown", last_ip=ip, is_trusted=False,
            )
            self.db.add(device)
        else:
            device.last_seen_at = datetime.now(timezone.utc)
            device.last_ip = ip
        await self.db.flush()
        return device

    async def _enforce_session_limit(self, user_id: str) -> None:
        result = await self.db.execute(
            select(Session).where(
                Session.user_id == user_id, Session.is_active == True  # noqa: E712
            ).order_by(Session.last_used_at.asc())
        )
        sessions = list(result.scalars().all())
        excess = len(sessions) - settings.max_concurrent_sessions + 1
        for s in sessions[:max(excess, 0)]:
            s.is_active = False
            s.revoked_at = datetime.now(timezone.utc)
            s.revoked_reason = "session_limit"
        if excess > 0:
            await self.db.commit()

    def _verify_totp(self, user: User, code: str) -> bool:
        if not user.mfa_secret_encrypted:
            return False
        try:
            secret = _encryption.decrypt(user.mfa_secret_encrypted)
        except Exception:
            return False
        return pyotp.TOTP(secret).verify(code, valid_window=1)

    async def _issue_tokens(
        self, user: User, ip_address: str, user_agent: str,
        device: Device | None = None, mfa_verified: bool = False,
    ) -> TokenResponse:
        identity = Identity(
            actor_id=user.id, actor_type=ActorType(user.primary_role if user.primary_role in ActorType._value2member_map_ else "CONSUMER"),
            primary_identifier=user.email, display_name=user.email,
            roles=user.roles or [user.primary_role],
            status="active" if user.is_active and not user.is_locked else "suspended",
            mfa_enabled=user.mfa_enabled,
            trust_score=user.trust_score,
            organization_id=user.organization_id,
            assigned_stores=user.assigned_stores,
            assigned_jurisdictions=user.assigned_jurisdictions,
            consumer_level=user.consumer_level,
            seller_level=user.seller_level,
        )
        access_token, _ = create_access_token(identity, jwt_secret=settings.jwt_secret)
        refresh_token, _, family_id = create_refresh_token(
            identity, jwt_secret=settings.jwt_secret,
        )
        now = datetime.now(timezone.utc)
        session = Session(
            id=str(uuid.uuid4()),
            user_id=user.id, refresh_token_hash=hash_token(refresh_token),
            token_family_id=family_id, ip_address=ip_address, user_agent=user_agent,
            device_id=device.id if device else None,
            is_active=True,
            expires_at=now + timedelta(minutes=settings.session_idle_timeout_minutes),
            absolute_expires_at=now + timedelta(hours=settings.session_absolute_timeout_hours),
        )
        self.db.add(session)
        await self.db.commit()
        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user_id=user.id, email=user.email, roles=user.roles,
            primary_role=user.primary_role, mfa_verified=mfa_verified,
        )

    async def _publish(self, event_type: str, payload: dict, severity: str = "info") -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-identity")
            await self.producer.publish("identity.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
