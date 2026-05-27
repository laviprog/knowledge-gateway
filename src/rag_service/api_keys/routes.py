from uuid import UUID

from fastapi import APIRouter

from rag_service.api_keys.dependencies import ApiKeyServiceDep
from rag_service.api_keys.schema import ApiKey
from rag_service.exceptions.responses import (
    auth_responses,
    internal_server_error_response,
    not_found_response,
)
from rag_service.security.dependencies import AdminApiKeyDep

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


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
    admin_id: AdminApiKeyDep,
    api_key_service: ApiKeyServiceDep,
) -> ApiKey:
    api_key_model = await api_key_service.revoke(
        api_key_id=api_key_id,
    )
    return ApiKey.model_validate(api_key_model)
