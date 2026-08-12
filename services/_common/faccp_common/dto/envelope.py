"""
Standard Response Envelopes as codified in Article 5 (§5.2) of the System Constitution.
"""

from __future__ import annotations

from typing import Any, Generic, Literal, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageInfo(BaseModel):
    total_items: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class SuccessResponse(BaseModel, Generic[T]):
    success: Literal[True] = True
    data: T
    message: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class ErrorDetail(BaseModel):
    code: str  # SCREAMING_SNAKE_CASE
    message: str  # Human-readable description
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None
    documentation_url: str | None = None


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error: ErrorDetail


class PaginatedResponse(BaseModel, Generic[T]):
    success: Literal[True] = True
    items: list[T]
    page_info: PageInfo
    meta: dict[str, Any] = Field(default_factory=dict)
