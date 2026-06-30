import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

from rag_service.config import settings
from rag_service.log_config import get_log
from rag_service.utils import generate_uuid

log = get_log(__name__)

# Frequently-polled endpoints excluded from request logging to avoid log spam.
_SILENT_PATHS = frozenset({"/metrics", "/healthcheck", "/healthcheck/ready"})


class LogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming HTTP requests and their responses.
    It captures details such as correlation ID, HTTP method, path, IP address,
    response status code, and duration of the request processing.
    """

    async def dispatch(self, request, call_next):
        if request.url.path in _SILENT_PATHS:
            return await call_next(request)

        correlation_id = request.headers.get("X-Request-Id") or generate_uuid()
        direct_ip = request.client.host if request.client else None
        if direct_ip and direct_ip in settings.TRUSTED_PROXY_IPS:
            ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or direct_ip
        else:
            ip = direct_ip

        # Bind context variables for structured logging
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
            ip_address=ip,
        )

        start = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
            return response
        except Exception:
            log.exception(
                "Unhandled Exception",
                request_method=request.method,
                request_url=str(request.url),
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            status = getattr(response, "status_code", None)
            log.info("Request completed", status_code=status, duration_ms=duration_ms)

            if response is not None:
                response.headers.setdefault("X-Request-Id", correlation_id)

            # unbind context variables
            structlog.contextvars.unbind_contextvars(
                "correlation_id", "method", "path", "ip_address"
            )
