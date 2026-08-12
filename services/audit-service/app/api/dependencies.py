"""FastAPI dependencies for audit service."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db

from app.services.audit_service import AuditService


def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    return get_db()


def get_audit_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuditService:
    return AuditService(db=db)
