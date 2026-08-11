from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard success API envelope."""

    success: bool = True
    data: T
    meta: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, str | int | float | bool | list[str]] = Field(default_factory=dict)


class APIErrorResponse(BaseModel):
    """Standard error API envelope."""

    success: bool = False
    error: ErrorDetail


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated list response."""

    items: list[T]
    pagination: PaginationMeta


def paginated(
    items: list[T], page: int, page_size: int, total_items: int
) -> PaginatedResponse[T]:
    """Helper to build a paginated response."""
    total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
    return PaginatedResponse(
        items=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        ),
    )
