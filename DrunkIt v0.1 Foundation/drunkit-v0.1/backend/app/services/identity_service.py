"""Identity domain service managing user registration, authentication, and RBAC roles."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    UnauthorizedError,
    ValidationError,
)
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.uow import SyncUnitOfWork
from app.models.identity import ConsumerProfile, Role, User
from app.schemas.auth import UserLoginRequest, UserRegisterRequest
from app.settings import settings


class IdentityService:
    """Service handling identity lifecycle, authentication, and role assignments."""

    @staticmethod
    def _get_or_create_role(role_code: str, session: Session) -> Role:
        """Fetch an existing role or create it if not yet present."""
        code_upper = role_code.strip().upper()
        role = session.scalars(select(Role).where(Role.code == code_upper)).first()
        if not role:
            role = Role(code=code_upper)
            session.add(role)
            session.flush()
        return role

    @classmethod
    def register_user(
        cls,
        request: UserRegisterRequest,
        uow: SyncUnitOfWork,
        correlation_id: uuid.UUID | None = None,
    ) -> User:
        """Register a new user account with assigned role and profile."""
        if not request.email and not request.phone:
            raise ValidationError("Either email or phone number must be provided for registration.")

        session = uow.session

        # 1. Check for duplicate email
        if request.email:
            existing_email = session.scalars(select(User).where(User.email == request.email)).first()
            if existing_email:
                raise ConflictError("A user with this email address already exists.")

        # 2. Check for duplicate phone
        if request.phone:
            existing_phone = session.scalars(select(User).where(User.phone == request.phone)).first()
            if existing_phone:
                raise ConflictError("A user with this phone number already exists.")

        # 3. Create User instance
        password_hash = get_password_hash(request.password)
        user = User(
            email=request.email,
            phone=request.phone,
            password_hash=password_hash,
            status="ACTIVE",
        )

        # 4. Attach Role
        target_role = cls._get_or_create_role(request.role, session)
        user.roles.append(target_role)
        session.add(user)
        session.flush()

        # 5. Attach Consumer Profile if registering as CONSUMER
        if target_role.code == "CONSUMER":
            profile = ConsumerProfile(
                user_id=user.id,
                preferred_market=request.preferred_market,
                date_of_birth_verified=False,
            )
            session.add(profile)
            session.flush()

        # 6. Record Audit and Publish Outbox Event
        uow.record_audit(
            actor_id=user.id,
            action="USER_REGISTERED",
            entity_type="User",
            entity_id=user.id,
            correlation_id=correlation_id,
            metadata={
                "email": user.email,
                "phone": user.phone,
                "role": target_role.code,
            },
        )
        uow.publish_outbox(
            event_type="USER_REGISTERED",
            aggregate_type="User",
            aggregate_id=user.id,
            correlation_id=correlation_id,
            payload={
                "user_id": str(user.id),
                "email": user.email,
                "phone": user.phone,
                "roles": [target_role.code],
            },
        )

        return user

    @classmethod
    def authenticate_user(
        cls,
        request: UserLoginRequest,
        uow: SyncUnitOfWork,
        correlation_id: uuid.UUID | None = None,
    ) -> tuple[User, str, int]:
        """Authenticate a user principal and generate a signed JWT access token."""
        if not request.email and not request.phone:
            raise ValidationError("Either email or phone must be provided to log in.")

        session = uow.session
        query = (
            select(User)
            .options(selectinload(User.roles), selectinload(User.consumer_profile))
        )

        if request.email:
            query = query.where(User.email == request.email)
        elif request.phone:
            query = query.where(User.phone == request.phone)

        user = session.scalars(query).first()
        if not user or not user.password_hash or not verify_password(request.password, user.password_hash):
            raise UnauthorizedError(
                message="Invalid email/phone or password provided.",
                code="INVALID_CREDENTIALS",
            )

        if user.status != "ACTIVE":
            raise ForbiddenError(
                message="Your account is not active. Please contact support.",
                code="ACCOUNT_INACTIVE",
            )

        # Generate JWT Token
        role_codes = [r.code for r in user.roles]
        token = create_access_token(
            subject=user.id,
            roles=role_codes,
            extra_claims={"email": user.email, "phone": user.phone},
        )
        expires_in = settings.access_token_expire_minutes * 60

        # Record Login Audit and Event
        uow.record_audit(
            actor_id=user.id,
            action="AUTH_LOGIN_SUCCEEDED",
            entity_type="User",
            entity_id=user.id,
            correlation_id=correlation_id,
            metadata={"roles": role_codes},
        )
        uow.publish_outbox(
            event_type="AUTH_LOGIN_SUCCEEDED",
            aggregate_type="User",
            aggregate_id=user.id,
            correlation_id=correlation_id,
            payload={
                "user_id": str(user.id),
                "roles": role_codes,
            },
        )

        return user, token, expires_in

    @staticmethod
    def get_user_by_id(user_id: uuid.UUID, session: Session) -> User | None:
        """Retrieve user by UUID with eagerly loaded roles and profile."""
        return session.scalars(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles), selectinload(User.consumer_profile))
        ).first()
