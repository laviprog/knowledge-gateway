from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src import log
from src.exceptions.domain import NotFoundError


def setup_exception_handlers(app: FastAPI):
    """
    Sets up custom exception handlers for the FastAPI application.
    """

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        log.error(
            "NotFoundError",
            request_method=request.method,
            request_url=str(request.url),
            detail=exc.detail,
        )

        return JSONResponse(
            status_code=404,
            content={
                "detail": exc.detail,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.error(
            "HTTPException",
            request_method=request.method,
            request_url=str(request.url),
            detail=exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers or {},
            content={
                "detail": exc.detail,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        log.error(
            "RequestValidationError",
            request_method=request.method,
            request_url=str(request.url),
            detail=exc.errors(),
        )

        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.error(
            "Unhandled Exception",
            request_method=request.method,
            request_url=str(request.url),
            detail=str(exc),
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )
