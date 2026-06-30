from uuid import UUID

from fastapi import APIRouter, status

from rag_service.documents.dependencies import DocumentServiceDep
from rag_service.exceptions.responses import (
    auth_responses,
    conflict_response,
    internal_server_error_response,
    not_found_response,
    validation_error_response,
)
from rag_service.knowledge_bases.dependencies import KnowledgeBaseServiceDep
from rag_service.knowledge_bases.schema import (
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBasesList,
    KnowledgeBaseUpdate,
)
from rag_service.pagination import PaginationDep
from rag_service.security.dependencies import AdminApiKeyDep
from rag_service.utils import is_dev_env

router = APIRouter(
    prefix="/knowledge-bases", tags=["Knowledge Bases"], include_in_schema=is_dev_env()
)


@router.get(
    path="",
    description="Get knowledge bases",
    responses={
        200: {
            "description": "Returns knowledge bases",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_knowledge_bases(
    admin_id: AdminApiKeyDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
    pagination: PaginationDep,
) -> KnowledgeBasesList:
    knowledge_base_list, total = await knowledge_base_service.list_paginated(
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return KnowledgeBasesList(
        knowledge_bases=[KnowledgeBase.model_validate(kb) for kb in knowledge_base_list],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    path="/{knowledge_base_id}",
    description="Get a knowledge base by id",
    responses={
        200: {
            "description": "Returns a knowledge base",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def get_knowledge_base(
    knowledge_base_id: UUID,
    admin_id: AdminApiKeyDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
) -> KnowledgeBase:
    knowledge_base = await knowledge_base_service.get_by_id_or_raise(knowledge_base_id)
    return KnowledgeBase.model_validate(knowledge_base)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    description="Create a knowledge base",
    responses={
        201: {
            "description": "Knowledge base has been created",
        },
        **auth_responses,
        **conflict_response,
        **not_found_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_knowledge_base(
    knowledge_base_create: KnowledgeBaseCreate,
    admin_id: AdminApiKeyDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
) -> KnowledgeBase:
    knowledge_base = await knowledge_base_service.create_knowledge_base(
        public_id=knowledge_base_create.public_id,
        name=knowledge_base_create.name,
        embedding_model_id=knowledge_base_create.embedding_model_id,
        description=knowledge_base_create.description,
    )
    return KnowledgeBase.model_validate(knowledge_base)


@router.patch(
    path="/{knowledge_base_id}",
    description="Update a knowledge base",
    responses={
        200: {
            "description": "Knowledge base has been updated",
        },
        **auth_responses,
        **not_found_response,
        **conflict_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def update_knowledge_base(
    knowledge_base_id: UUID,
    knowledge_base_update: KnowledgeBaseUpdate,
    admin_id: AdminApiKeyDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
) -> KnowledgeBase:
    knowledge_base = await knowledge_base_service.update_knowledge_base(
        knowledge_base_id=knowledge_base_id,
        public_id=knowledge_base_update.public_id,
        name=knowledge_base_update.name,
        description=knowledge_base_update.description,
    )
    return KnowledgeBase.model_validate(knowledge_base)


@router.delete(
    path="/{knowledge_base_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a knowledge base",
    responses={
        204: {
            "description": "Knowledge base has been deleted",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def delete_knowledge_base(
    knowledge_base_id: UUID,
    admin_id: AdminApiKeyDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
    document_service: DocumentServiceDep,
) -> None:
    # Cascade: documents belong to exactly one knowledge base, so they (and their vectors) are
    # removed together with it; otherwise they would be orphaned and leak vectors in Qdrant.
    knowledge_base = await knowledge_base_service.get_by_id_or_raise(knowledge_base_id)
    await document_service.delete_documents_for_knowledge_base(knowledge_base)
    await knowledge_base_service.delete_knowledge_base(knowledge_base_id)
