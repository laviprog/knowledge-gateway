from uuid import UUID

from fastapi import APIRouter, status

from rag_service.exceptions.responses import (
    auth_responses,
    conflict_response,
    internal_server_error_response,
    not_found_response,
    validation_error_response,
)
from rag_service.llm_models.dependencies import LlmModelServiceDep
from rag_service.llm_models.schema import (
    LlmModel,
    LlmModelCreate,
    LlmModelsList,
    LlmModelUpdate,
    OpenAIModel,
    OpenAIModelsList,
)
from rag_service.pagination import PaginationDep
from rag_service.security.dependencies import AdminDep, UserApiKeyDep
from rag_service.utils import is_dev_env

llm_models_router = APIRouter(
    prefix="/llm-models", tags=["LLM Models"], include_in_schema=is_dev_env()
)
models_router = APIRouter(prefix="/models", tags=["Models"])


@llm_models_router.get(
    path="",
    description="Get LLM models",
    responses={
        200: {
            "description": "Returns LLM models",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_llm_models(
    admin_id: AdminDep,
    llm_model_service: LlmModelServiceDep,
    pagination: PaginationDep,
) -> LlmModelsList:
    model_list, total = await llm_model_service.list_paginated(
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return LlmModelsList(
        models=[LlmModel.model_validate(model) for model in model_list],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@llm_models_router.get(
    path="/{model_id}",
    description="Get an LLM model by id",
    responses={
        200: {
            "description": "Returns an LLM model",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def get_llm_model(
    model_id: UUID,
    admin_id: AdminDep,
    llm_model_service: LlmModelServiceDep,
) -> LlmModel:
    model = await llm_model_service.get_by_id_or_raise(model_id)
    return LlmModel.model_validate(model)


@llm_models_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    description="Create an LLM model",
    responses={
        201: {
            "description": "LLM model has been created",
        },
        **auth_responses,
        **conflict_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_llm_model(
    model_create: LlmModelCreate,
    admin_id: AdminDep,
    llm_model_service: LlmModelServiceDep,
) -> LlmModel:
    model = await llm_model_service.create_model(
        public_id=model_create.public_id,
        provider=model_create.provider,
        provider_model=model_create.provider_model,
        context_window_tokens=model_create.context_window_tokens,
        max_completion_tokens=model_create.max_completion_tokens,
        provider_id=model_create.provider_id,
        description=model_create.description,
    )
    return LlmModel.model_validate(model)


@llm_models_router.patch(
    path="/{model_id}",
    description="Update an LLM model",
    responses={
        200: {
            "description": "LLM model has been updated",
        },
        **auth_responses,
        **not_found_response,
        **conflict_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def update_llm_model(
    model_id: UUID,
    model_update: LlmModelUpdate,
    admin_id: AdminDep,
    llm_model_service: LlmModelServiceDep,
) -> LlmModel:
    model = await llm_model_service.update_model(
        model_id=model_id,
        public_id=model_update.public_id,
        provider=model_update.provider,
        provider_model=model_update.provider_model,
        context_window_tokens=model_update.context_window_tokens,
        max_completion_tokens=model_update.max_completion_tokens,
        provider_id=model_update.provider_id,
        description=model_update.description,
    )
    return LlmModel.model_validate(model)


@llm_models_router.delete(
    path="/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an LLM model",
    responses={
        204: {
            "description": "LLM model has been deleted",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def delete_llm_model(
    model_id: UUID,
    admin_id: AdminDep,
    llm_model_service: LlmModelServiceDep,
) -> None:
    await llm_model_service.delete_model(model_id)


@models_router.get(
    path="",
    description="Get OpenAI-compatible model list",
    responses={
        200: {
            "description": "Returns available models",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_openai_models(
    user_id: UserApiKeyDep,
    llm_model_service: LlmModelServiceDep,
) -> OpenAIModelsList:
    model_list = await llm_model_service.list_not_deleted()
    return OpenAIModelsList(
        data=[
            OpenAIModel(
                id=model.public_id,
                created=int(model.created_at.timestamp()),
            )
            for model in model_list
        ],
    )
