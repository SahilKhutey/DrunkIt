"""Support agent service — database models."""

from __future__ import annotations
from datetime import datetime
from typing import Any
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class Conversation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "support_conversations"

    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), default="New conversation", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)


class Message(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "support_messages"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("support_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class KnowledgeDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_documents"

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tags: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class SupportTicket(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "support_tickets"

    ticket_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    subject: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="OPEN", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(32), default="NORMAL", nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(36), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="AI_AGENT", nullable=False)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
