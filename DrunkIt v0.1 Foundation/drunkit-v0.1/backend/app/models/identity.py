"""Identity domain models for users, roles, and consumer profiles."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    """Core user account representing consumers, staff, brand managers, and admins."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
    consumer_profile: Mapped["ConsumerProfile | None"] = relationship(
        "ConsumerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Role(Base):
    """Role definition for Role-Based Access Control (RBAC)."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
    )


class UserRole(Base):
    """Association table mapping users to roles."""

    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )


class ConsumerProfile(Base):
    """Consumer profile containing market preferences and age verification flags."""

    __tablename__ = "consumer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    preferred_market: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_of_birth_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="consumer_profile")
