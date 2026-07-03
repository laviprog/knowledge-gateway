from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from knowledge_gateway.exceptions.domain import AppError
from knowledge_gateway.log_config import get_log
from knowledge_gateway.utils import utc_now_iso

log = get_log(__name__)


def setup_exception_handlers(app: FastAPI):
    """
    Sets up custom exception handlers for the FastAPI application.
    """

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        log.warning(
            exc.__class__.__name__,
            request_method=request.method,
            request_url=str(request.url),
            code=exc.code,
            detail=exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "detail": exc.detail,
                "timestamp": utc_now_iso(),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.warning(
            "HTTPException",
            request_method=request.method,
            request_url=str(request.url),
            status_code=exc.status_code,
            detail=exc.detail,
        )

        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers or {},
            content={
                "code": "http_error",
                "detail": str(exc.detail),
                "timestamp": utc_now_iso(),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        log.warning(
            "RequestValidationError",
            request_method=request.method,
            request_url=str(request.url),
            detail=exc.errors(),
        )

        return JSONResponse(
            status_code=422,
            content={
                "code": "validation_error",
                "detail": exc.errors(),
                "timestamp": utc_now_iso(),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        log.exception(
            "Unhandled exception",
            request_method=request.method,
            request_url=str(request.url),
            detail=str(exc),
        )

        return JSONResponse(
            status_code=500,
            content={
                "code": "internal_server_error",
                "detail": "An unexpected error occurred",
                "timestamp": utc_now_iso(),
            },
        )
