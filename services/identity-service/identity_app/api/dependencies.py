from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from faccp_common.database import get_db
from faccp_common.exceptions import UnauthorizedError
from faccp_common.security import decode_token
from identity_app.config import get_settings
from identity_app.db.models import Account

security_scheme = HTTPBearer(auto_error=True)
settings = get_settings()


async def get_current_account(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Account:
    """Validate bearer token and resolve account with roles."""
    try:
        payload = decode_token(
            token.credentials,
            secret=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            expected_type="access",
        )
        account_id: str = payload["sub"]
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired access token.") from exc

    res = await db.execute(
        select(Account).options(selectinload(Account.roles)).where(Account.id == account_id)
    )
    account = res.scalar_one_or_none()
    if not account:
        raise UnauthorizedError("Account no longer exists.")
    return account
