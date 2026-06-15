from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header

from rag_service.api_keys.dependencies import ApiKeyServiceDep
from rag_service.api_keys.models import ApiKeyModel
from rag_service.exceptions import PermissionDeniedError, UnauthorizedError
from rag_service.users.models import Role


@dataclass(frozen=True)
class AuthContext:
    """
    Authenticated API key context.
    """

    user_id: UUID
    api_key_id: UUID
    requests_per_minute: int


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
