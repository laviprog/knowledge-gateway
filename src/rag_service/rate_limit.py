from slowapi import Limiter
from starlette.requests import Request
from starlette.responses import JSONResponse

from rag_service.security.api_keys import hash_api_key


def _key_func(request: Request) -> str:
    """
    Rate limit key: HMAC hash of the Bearer token.
    Unique regardless of prefix length, does not store the raw key in memory.
    Requests without a valid Bearer token are bucketed together — they fail auth anyway.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
        if token:
            return hash_api_key(token)
    return "unauthenticated"


limiter = Limiter(key_func=_key_func)


def rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "message": "Rate limit exceeded. Please slow down your requests.",
                "type": "rate_limit_error",
                "code": "rate_limit_exceeded",
            }
        },
    )
