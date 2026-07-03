from uuid import UUID

from fastapi import APIRouter, status

from knowledge_gateway.embedding_models.dependencies import EmbeddingModelServiceDep
from knowledge_gateway.embedding_models.schema import (
    EmbeddingModel,
    EmbeddingModelCreate,
    EmbeddingModelsList,
    EmbeddingModelUpdate,
)
from knowledge_gateway.exceptions.responses import (
    auth_responses,
    conflict_response,
    internal_server_error_response,
    not_found_response,
    validation_error_response,
)
from knowledge_gateway.pagination import PaginationDep
from knowledge_gateway.security.dependencies import AdminDep
from knowledge_gateway.utils import is_dev_env

router = APIRouter(
    prefix="/embedding-models", tags=["Embedding Models"], include_in_schema=is_dev_env()
)


@router.get(
    path="",
    description="Get embedding models",
    responses={
        200: {
            "description": "Returns embedding models",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_embedding_models(
    admin_id: AdminDep,
    embedding_model_service: EmbeddingModelServiceDep,
    pagination: PaginationDep,
) -> EmbeddingModelsList:
    model_list, total = await embedding_model_service.list_paginated(
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return EmbeddingModelsList(
        models=[EmbeddingModel.model_validate(model) for model in model_list],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    path="/{model_id}",
    description="Get an embedding model by id",
    responses={
        200: {
            "description": "Returns an embedding model",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def get_embedding_model(
    model_id: UUID,
    admin_id: AdminDep,
    embedding_model_service: EmbeddingModelServiceDep,
) -> EmbeddingModel:
    model = await embedding_model_service.get_by_id_or_raise(model_id)
    return EmbeddingModel.model_validate(model)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    description="Create an embedding model",
    responses={
        201: {
            "description": "Embedding model has been created",
        },
        **auth_responses,
        **conflict_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_embedding_model(
    model_create: EmbeddingModelCreate,
    admin_id: AdminDep,
    embedding_model_service: EmbeddingModelServiceDep,
) -> EmbeddingModel:
    model = await embedding_model_service.create_embedding_model(
        public_id=model_create.public_id,
        provider_model=model_create.provider_model,
        dimension=model_create.dimension,
        collection_name=model_create.collection_name,
        provider_id=model_create.provider_id,
        description=model_create.description,
    )
    return EmbeddingModel.model_validate(model)


@router.patch(
    path="/{model_id}",
    description="Update an embedding model",
    responses={
        200: {
            "description": "Embedding model has been updated",
        },
        **auth_responses,
        **not_found_response,
        **conflict_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def update_embedding_model(
    model_id: UUID,
    model_update: EmbeddingModelUpdate,
    admin_id: AdminDep,
    embedding_model_service: EmbeddingModelServiceDep,
) -> EmbeddingModel:
    model = await embedding_model_service.update_embedding_model(
        model_id=model_id,
        public_id=model_update.public_id,
        provider_model=model_update.provider_model,
        dimension=model_update.dimension,
        provider_id=model_update.provider_id,
        description=model_update.description,
    )
    return EmbeddingModel.model_validate(model)


@router.delete(
    path="/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an embedding model",
    responses={
        204: {
            "description": "Embedding model has been deleted",
        },
        **auth_responses,
        **not_found_response,
        **conflict_response,
        **internal_server_error_response,
    },
)
async def delete_embedding_model(
    model_id: UUID,
    admin_id: AdminDep,
    embedding_model_service: EmbeddingModelServiceDep,
) -> None:
    await embedding_model_service.delete_embedding_model(model_id)
