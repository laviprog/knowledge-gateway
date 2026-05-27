from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header

from rag_service.api_keys.dependencies import ApiKeyServiceDep
from rag_service.api_keys.models import ApiKeyModel
from rag_service.exceptions import PermissionDeniedError, UnauthorizedError
from rag_service.users.models import Role


async def require_admin_key(
    api_key_service: ApiKeyServiceDep,
    authorization: str | None = Header(default=None),
) -> UUID:
    api_key_model = await _verify_api_key(api_key_service, authorization)
    user = api_key_model.user
    if user.role != Role.ADMIN:
        raise PermissionDeniedError()
    return user.id


async def require_user_key(
    api_key_service: ApiKeyServiceDep,
    authorization: str | None = Header(default=None),
) -> UUID:
    api_key_model = await _verify_api_key(api_key_service, authorization)
    return api_key_model.user.id


async def _verify_api_key(
    api_key_service: ApiKeyServiceDep, authorization: str | None
) -> ApiKeyModel:
    """
    Verify the API key from the Authorization header and return the associated API key ID.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError()

    api_key_value = authorization.removeprefix("Bearer ").strip()

    api_key = await api_key_service.validate_api_key(api_key_value)

    if not api_key:
        raise UnauthorizedError()

    return api_key


type UserApiKeyDep = Annotated[UUID, Depends(require_user_key)]
type AdminApiKeyDep = Annotated[UUID, Depends(require_admin_key)]
