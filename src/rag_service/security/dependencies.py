from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, Header

from rag_service.api_keys.dependencies import ApiKeyServiceDep
from rag_service.api_keys.models import ApiKeyModel
from rag_service.auth.session_store import resolve_session_user_id
from rag_service.config import settings
from rag_service.exceptions import PermissionDeniedError, UnauthorizedError
from rag_service.users.dependencies import UserServiceDep
from rag_service.users.models import Role


@dataclass(frozen=True)
class AuthContext:
    """
    Authenticated API key context.
    """

    user_id: UUID
    api_key_id: UUID
    requests_per_minute: int


@dataclass(frozen=True)
class AdminContext:
    """
    Authenticated admin context, from either an interactive session or an admin API key.
    """

    user_id: UUID


async def require_admin_key(
    api_key_service: ApiKeyServiceDep,
    authorization: str | None = Header(default=None),
) -> AuthContext:
    api_key_model = await _verify_api_key(api_key_service, authorization)
    user = api_key_model.user
    if user.role != Role.ADMIN:
        raise PermissionDeniedError()
    return AuthContext(
        user_id=user.id,
        api_key_id=api_key_model.id,
        requests_per_minute=user.requests_per_minute,
    )


async def require_user_key(
    api_key_service: ApiKeyServiceDep,
    authorization: str | None = Header(default=None),
) -> AuthContext:
    api_key_model = await _verify_api_key(api_key_service, authorization)
    user = api_key_model.user
    return AuthContext(
        user_id=user.id,
        api_key_id=api_key_model.id,
        requests_per_minute=user.requests_per_minute,
    )


async def _resolve_admin_session(
    user_service: UserServiceDep, session_token: str | None
) -> AdminContext | None:
    """
    Resolve an admin from a session cookie, or None when the session is absent/invalid or the
    user is not an active admin.
    """
    if not session_token:
        return None

    user_id = await resolve_session_user_id(session_token)
    if user_id is None:
        return None

    user = await user_service.get_active_or_none(user_id)
    if user is None or user.role != Role.ADMIN:
        return None

    return AdminContext(user_id=user.id)


async def require_admin_session(
    user_service: UserServiceDep,
    session_token: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
) -> AdminContext:
    """
    Require a valid admin session cookie. Used by admin-panel-only routes (e.g. /auth/me).
    """
    context = await _resolve_admin_session(user_service, session_token)
    if context is None:
        raise UnauthorizedError()
    return context


async def require_admin(
    api_key_service: ApiKeyServiceDep,
    user_service: UserServiceDep,
    authorization: str | None = Header(default=None),
    session_token: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
) -> AdminContext:
    """
    Require admin access via either an interactive session cookie or an admin API key.

    The session is tried first (admin panel); the Bearer key is the fallback (scripts/CI).
    """
    context = await _resolve_admin_session(user_service, session_token)
    if context is not None:
        return context

    api_key_model = await _verify_api_key(api_key_service, authorization)
    user = api_key_model.user
    if user.role != Role.ADMIN:
        raise PermissionDeniedError()
    return AdminContext(user_id=user.id)


async def _verify_api_key(
    api_key_service: ApiKeyServiceDep, authorization: str | None
) -> ApiKeyModel:
    """
    Verify the API key from the Authorization header and return the associated API key.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError()

    api_key_value = authorization.removeprefix("Bearer ").strip()

    api_key = await api_key_service.validate_api_key(api_key_value)

    if not api_key:
        raise UnauthorizedError()

    return api_key


type UserApiKeyDep = Annotated[AuthContext, Depends(require_user_key)]
type AdminApiKeyDep = Annotated[AuthContext, Depends(require_admin_key)]
type AdminDep = Annotated[AdminContext, Depends(require_admin)]
type AdminSessionDep = Annotated[AdminContext, Depends(require_admin_session)]
