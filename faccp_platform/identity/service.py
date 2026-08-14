"""Identity service managing user registration and authentication."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.database.models import User
from faccp_platform.security.password import hash_password, verify_password
from faccp_platform.security.policies import validate_password


class IdentityService:
    """Identity service encapsulation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_email(self, email: str) -> User | None:
        """Locate user by lowercase email address."""
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def register(
        self,
        *,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Validate password policy, ensure email uniqueness, and persist user."""
        validate_password(password)
        existing = await self.find_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=email.lower(),
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def authenticate(self, *, email: str, password: str) -> User | None:
        """Verify user status and password credentials."""
        user = await self.find_by_email(email)
        if user is None:
            return None

        if user.status != "active":
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user
