from uuid import UUID

from fastapi import APIRouter, status

from rag_service.exceptions.responses import (
    auth_responses,
    conflict_response,
    internal_server_error_response,
    not_found_response,
    validation_error_response,
)
from rag_service.pagination import PaginationDep
from rag_service.providers.dependencies import ProviderServiceDep
from rag_service.providers.schema import (
    Provider,
    ProviderCreate,
    ProvidersList,
    ProviderUpdate,
)
from rag_service.security.dependencies import AdminDep
from rag_service.utils import is_dev_env

router = APIRouter(prefix="/providers", tags=["Providers"], include_in_schema=is_dev_env())


@router.get(
    path="",
    description="Get inference providers",
    responses={
        200: {
            "description": "Returns inference providers",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_providers(
    admin_id: AdminDep,
    provider_service: ProviderServiceDep,
    pagination: PaginationDep,
) -> ProvidersList:
    provider_list, total = await provider_service.list_paginated(
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return ProvidersList(
        providers=[Provider.from_model(provider) for provider in provider_list],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    path="/{provider_id}",
    description="Get an inference provider by id",
    responses={
        200: {
            "description": "Returns an inference provider",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def get_provider(
    provider_id: UUID,
    admin_id: AdminDep,
    provider_service: ProviderServiceDep,
) -> Provider:
    provider = await provider_service.get_by_id_or_raise(provider_id)
    return Provider.from_model(provider)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    description="Create an inference provider",
    responses={
        201: {
            "description": "Inference provider has been created",
        },
        **auth_responses,
        **conflict_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_provider(
    provider_create: ProviderCreate,
    admin_id: AdminDep,
    provider_service: ProviderServiceDep,
) -> Provider:
    provider = await provider_service.create_provider(
        public_id=provider_create.public_id,
        base_url=provider_create.base_url,
        api_key=provider_create.api_key,
        timeout_seconds=provider_create.timeout_seconds,
        max_retries=provider_create.max_retries,
        description=provider_create.description,
    )
    return Provider.from_model(provider)


@router.patch(
    path="/{provider_id}",
    description="Update an inference provider",
    responses={
        200: {
            "description": "Inference provider has been updated",
        },
        **auth_responses,
        **not_found_response,
        **conflict_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def update_provider(
    provider_id: UUID,
    provider_update: ProviderUpdate,
    admin_id: AdminDep,
    provider_service: ProviderServiceDep,
) -> Provider:
    provider = await provider_service.update_provider(
        provider_id=provider_id,
        public_id=provider_update.public_id,
        base_url=provider_update.base_url,
        api_key=provider_update.api_key,
        timeout_seconds=provider_update.timeout_seconds,
        max_retries=provider_update.max_retries,
        description=provider_update.description,
    )
    return Provider.from_model(provider)


@router.delete(
    path="/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an inference provider",
    responses={
        204: {
            "description": "Inference provider has been deleted",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def delete_provider(
    provider_id: UUID,
    admin_id: AdminDep,
    provider_service: ProviderServiceDep,
) -> None:
    await provider_service.delete_provider(provider_id)
