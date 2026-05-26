from uuid import UUID

from fastapi import APIRouter, status

from rag_service.api_keys.schema import ApiKey, ApiKeyCreate, ApiKeyCreated
from rag_service.exceptions.responses import (
    auth_responses,
    internal_server_error_response,
    not_found_response,
    validation_error_response,
)
from rag_service.security.dependencies import AdminApiKeyDep
from rag_service.users.dependencies import UserServiceDep
from rag_service.users.schema import User, UserCreate, UsersList

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    path="",
    description="Get a list of users",
    responses={
        200: {
            "description": "Returns a list of users",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_users(
    admin_id: AdminApiKeyDep,
    user_service: UserServiceDep,
) -> UsersList:
    user_models = await user_service.list_active()
    return UsersList(users=[User.model_validate(user_model) for user_model in user_models])


@router.get(
    path="/{user_id}",
    description="Get a user by id",
    responses={
        200: {
            "description": "Returns a user by id",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def get_user(
    user_id: UUID,
    admin_id: AdminApiKeyDep,
    user_service: UserServiceDep,
) -> User:
    user_model = await user_service.get_by_id_or_raise(user_id)
    return User.model_validate(user_model)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    description="Create a user",
    responses={
        201: {
            "description": "User has been created",
        },
        **auth_responses,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_user(
    user_create: UserCreate,
    admin_id: AdminApiKeyDep,
    user_service: UserServiceDep,
) -> User:
    user_model = await user_service.create_user(
        name=user_create.name,
        role=user_create.role,
    )
    return User.model_validate(user_model)


@router.post(
    path="/{user_id}/api-keys",
    status_code=status.HTTP_201_CREATED,
    description="Create an API key for a user",
    responses={
        201: {
            "description": "API key has been created",
        },
        **auth_responses,
        **not_found_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_api_key(
    user_id: UUID,
    admin_id: AdminApiKeyDep,
    user_service: UserServiceDep,
    api_key_create: ApiKeyCreate,
) -> ApiKeyCreated:
    api_key_model, api_key_value = await user_service.create_api_key_for_user(
        user_id=user_id,
        name=api_key_create.name,
        expires_at=api_key_create.expires_at,
    )
    return ApiKeyCreated(
        api_key=api_key_value,
        api_key_info=ApiKey.model_validate(api_key_model),
    )
