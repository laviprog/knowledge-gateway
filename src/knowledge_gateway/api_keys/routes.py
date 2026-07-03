from uuid import UUID

from fastapi import APIRouter

from knowledge_gateway.api_keys.dependencies import ApiKeyServiceDep
from knowledge_gateway.api_keys.schema import ApiKey
from knowledge_gateway.exceptions.responses import (
    auth_responses,
    internal_server_error_response,
    not_found_response,
)
from knowledge_gateway.security.dependencies import AdminDep
from knowledge_gateway.utils import is_dev_env

router = APIRouter(prefix="/api-keys", tags=["API Keys"], include_in_schema=is_dev_env())


@router.post(
    path="/{api_key_id}/revoke",
    description="Revoke an API key",
    responses={
        200: {
            "description": "API key has been revoked",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def revoke_api_key(
    api_key_id: UUID,
    admin_id: AdminDep,
    api_key_service: ApiKeyServiceDep,
) -> ApiKey:
    api_key_model = await api_key_service.revoke(
        api_key_id=api_key_id,
    )
    return ApiKey.model_validate(api_key_model)
