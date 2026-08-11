from __future__ import annotations

import base64
import io
from datetime import datetime, timedelta, timezone
from typing import Any

import pyotp
import qrcode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from faccp_common.exceptions import (
    ConflictError,
    InvalidCredentialsError,
    NotFoundError,
    UnauthorizedError,
)
from faccp_common.security import (
    FieldEncryption,
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    pseudonymize,
    verify_password,
)
from identity_app.config import get_settings
from identity_app.db.models import Account, AccountStatus, AccountType, RoleModel, Session
from identity_app.schemas.auth import (
    LoginRequest,
    MFAEnableResponse,
    RegisterRequest,
    TokenResponse,
)


class AuthService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()
        self.enc = FieldEncryption(self.settings.field_encryption_key)

    async def register(self, req: RegisterRequest) -> Account:
        existing = await self.db.execute(select(Account).where(Account.email == req.email))
        if existing.scalar_one_or_none():
            raise ConflictError("An account with this email already exists.")

        role_res = await self.db.execute(select(RoleModel).where(RoleModel.name == req.account_type))
        role = role_res.scalar_one_or_none()

        account = Account(
            email=req.email,
            password_hash=hash_password(req.password),
            account_type=AccountType(req.account_type),
            status=AccountStatus.ACTIVE,
        )

        if req.phone:
            account.phone_encrypted = self.enc.encrypt(req.phone)
            account.phone_hash = pseudonymize(req.phone)

        if role:
            account.roles.append(role)

        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account, ["roles"])
        return account

    async def login(
        self, req: LoginRequest, user_agent: str | None = None, ip_address: str | None = None
    ) -> TokenResponse:
        res = await self.db.execute(
            select(Account).options(selectinload(Account.roles)).where(Account.email == req.email)
        )
        account = res.scalar_one_or_none()
        if not account or not verify_password(req.password, account.password_hash):
            raise InvalidCredentialsError()

        if account.status != AccountStatus.ACTIVE:
            raise UnauthorizedError("Account is not active.")

        if account.mfa_enabled:
            if not req.mfa_code:
                raise UnauthorizedError("MFA code required.")
            secret = self.enc.decrypt(account.mfa_secret_encrypted)  # type: ignore[arg-type]
            totp = pyotp.TOTP(secret)
            if not totp.verify(req.mfa_code):
                raise InvalidCredentialsError("Invalid MFA code.")

        roles_list = [r.name for r in account.roles]

        access = create_access_token(
            subject=account.id,
            secret=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            issuer=self.settings.jwt_issuer,
            audience=self.settings.jwt_audience,
            expires_minutes=self.settings.jwt_access_token_expire_minutes,
            claims={"roles": roles_list, "email": account.email},
        )

        refresh = create_refresh_token(
            subject=account.id,
            secret=self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
            issuer=self.settings.jwt_issuer,
            audience=self.settings.jwt_audience,
            expires_days=self.settings.jwt_refresh_token_expire_days,
        )

        session = Session(
            account_id=account.id,
            refresh_token_hash=hash_token(refresh),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.settings.jwt_refresh_token_expire_days),
        )
        self.db.add(session)
        account.last_login_at = datetime.now(timezone.utc)
        account.last_login_ip = ip_address
        await self.db.commit()

        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=self.settings.jwt_access_token_expire_minutes * 60,
            user_id=account.id,
            roles=roles_list,
        )

    async def enable_mfa(self, account_id: str) -> MFAEnableResponse:
        res = await self.db.execute(select(Account).where(Account.id == account_id))
        account = res.scalar_one_or_none()
        if not account:
            raise NotFoundError("Account not found.")

        secret = pyotp.random_base32()
        account.mfa_secret_encrypted = self.enc.encrypt(secret)
        await self.db.commit()

        totp = pyotp.TOTP(secret)
        url = totp.provisioning_uri(name=account.email, issuer_name="FACCP Platform")

        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        return MFAEnableResponse(
            secret=secret,
            otpauth_url=url,
            qr_code_base64=f"data:image/png;base64,{qr_b64}",
        )

    async def verify_mfa_enable(self, account_id: str, code: str) -> bool:
        res = await self.db.execute(select(Account).where(Account.id == account_id))
        account = res.scalar_one_or_none()
        if not account or not account.mfa_secret_encrypted:
            raise NotFoundError("MFA setup not initiated.")

        secret = self.enc.decrypt(account.mfa_secret_encrypted)
        totp = pyotp.TOTP(secret)
        if not totp.verify(code):
            raise InvalidCredentialsError("Invalid OTP code.")

        account.mfa_enabled = True
        await self.db.commit()
        return True
