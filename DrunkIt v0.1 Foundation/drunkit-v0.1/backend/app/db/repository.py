"""Generic base repository for data access operations."""

import uuid
from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing standard data access operations."""

    def __init__(self, model: type[ModelType], session: Session | AsyncSession) -> None:
        self.model = model
        self.session = session

    # Synchronous operations
    def get_sync(self, id_: uuid.UUID) -> ModelType | None:
        """Fetch entity by primary key synchronously."""
        if not isinstance(self.session, Session):
            raise TypeError("get_sync requires a synchronous Session.")
        return self.session.get(self.model, id_)

    def list_sync(
        self,
        offset: int = 0,
        limit: int = 50,
        filters: Sequence[Any] | None = None,
    ) -> list[ModelType]:
        """List entities with pagination and optional filters synchronously."""
        if not isinstance(self.session, Session):
            raise TypeError("list_sync requires a synchronous Session.")
        query = select(self.model).offset(offset).limit(limit)
        if filters:
            for f in filters:
                query = query.where(f)
        return list(self.session.scalars(query).all())

    def add_sync(self, entity: ModelType) -> ModelType:
        """Add an entity to the session synchronously."""
        if not isinstance(self.session, Session):
            raise TypeError("add_sync requires a synchronous Session.")
        self.session.add(entity)
        return entity

    def delete_sync(self, entity: ModelType) -> None:
        """Delete an entity from the session synchronously."""
        if not isinstance(self.session, Session):
            raise TypeError("delete_sync requires a synchronous Session.")
        self.session.delete(entity)

    # Asynchronous operations
    async def get(self, id_: uuid.UUID) -> ModelType | None:
        """Fetch entity by primary key asynchronously."""
        if not isinstance(self.session, AsyncSession):
            raise TypeError("get requires an asynchronous AsyncSession.")
        return await self.session.get(self.model, id_)

    async def list(
        self,
        offset: int = 0,
        limit: int = 50,
        filters: Sequence[Any] | None = None,
    ) -> list[ModelType]:
        """List entities with pagination and optional filters asynchronously."""
        if not isinstance(self.session, AsyncSession):
            raise TypeError("list requires an asynchronous AsyncSession.")
        query = select(self.model).offset(offset).limit(limit)
        if filters:
            for f in filters:
                query = query.where(f)
        result = await self.session.scalars(query)
        return list(result.all())

    async def add(self, entity: ModelType) -> ModelType:
        """Add an entity to the session asynchronously."""
        if not isinstance(self.session, AsyncSession):
            raise TypeError("add requires an asynchronous AsyncSession.")
        self.session.add(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        """Delete an entity from the session asynchronously."""
        if not isinstance(self.session, AsyncSession):
            raise TypeError("delete requires an asynchronous AsyncSession.")
        await self.session.delete(entity)
