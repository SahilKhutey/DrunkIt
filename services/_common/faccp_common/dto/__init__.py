"""API Response Envelope DTOs as codified in Article 5 of the System Constitution (§5.2)."""
from .envelope import SuccessResponse, ErrorResponse, ErrorDetail, PaginatedResponse, PageInfo

__all__ = ["SuccessResponse", "ErrorResponse", "ErrorDetail", "PaginatedResponse", "PageInfo"]
