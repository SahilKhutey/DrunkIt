"""Generic Repository pattern implementation for SQLAlchemy models."""

from __future__ import annotations

from typing import Generic, Sequence, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic async repository for SQLAlchemy models."""

    def __init__(self, model_cls: Type[T], session: AsyncSession) -> None:
        self.model_cls = model_cls
        self.session = session

    async def get_by_id(self, id_val: Any) -> T | None:
        return await self.session.get(self.model_cls, id_val)

    async def create(self, **kwargs) -> T:
        instance = self.model_cls(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[T]:
        stmt = select(self.model_cls).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, instance: T) -> None:
        await self.session.delete(instance)
        await self.session.flush()
