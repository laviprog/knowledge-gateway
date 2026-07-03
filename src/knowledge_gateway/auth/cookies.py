from typing import Literal, cast

from fastapi import Response

from knowledge_gateway.config import settings


def set_session_cookie(response: Response, raw_token: str) -> None:
    """
    Attach the session cookie to the response. httpOnly so JavaScript can never read the token.
    """
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=raw_token,
        max_age=settings.SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=cast("Literal['strict', 'lax', 'none']", settings.SESSION_COOKIE_SAMESITE),
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    """
    Remove the session cookie (logout).
    """
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=cast("Literal['strict', 'lax', 'none']", settings.SESSION_COOKIE_SAMESITE),
        path="/",
    )
