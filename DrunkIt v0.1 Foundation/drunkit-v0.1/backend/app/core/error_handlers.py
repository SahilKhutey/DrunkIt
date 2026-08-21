"""Standardized error handlers conforming to the DrunkIt v0.1 API Specification."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import DrunkItError
from app.core.middleware import get_current_request_id

logger = logging.getLogger("drunkit.errors")


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    request_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Format and return a standardized JSON error envelope."""
    req_id = request_id or get_current_request_id()
    payload = {
        "error": {
            "code": code,
            "message": message,
            "request_id": req_id,
            "details": details or {},
        }
    }
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={"X-Request-ID": req_id},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI application instance."""

    @app.exception_handler(DrunkItError)
    async def drunkit_error_handler(request: Request, exc: DrunkItError) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None) or get_current_request_id()
        if exc.status_code >= 500:
            logger.error(
                "DrunkItError [%s]: %s (request_id=%s)",
                exc.code,
                exc.message,
                req_id,
                exc_info=True,
            )
        return create_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            request_id=req_id,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None) or get_current_request_id()
        errors = exc.errors()
        formatted_details = {
            "validation_errors": [
                {
                    "loc": list(err.get("loc", [])),
                    "msg": err.get("msg", "Invalid input"),
                    "type": err.get("type", "value_error"),
                }
                for err in errors
            ]
        }
        return create_error_response(
            code="VALIDATION_FAILED",
            message="Input data validation failed.",
            status_code=422,
            request_id=req_id,
            details=formatted_details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None) or get_current_request_id()
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "RESOURCE_NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")
        return create_error_response(
            code=code,
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=req_id,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None) or get_current_request_id()
        logger.exception("Unhandled server exception occurred (request_id=%s): %s", req_id, exc)
        return create_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred. Please contact support.",
            status_code=500,
            request_id=req_id,
        )
