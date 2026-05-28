from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, UploadFile, status

from rag_service.documents.dependencies import DocumentServiceDep
from rag_service.documents.extractors import extract_document_from_upload
from rag_service.documents.schema import (
    Document,
    DocumentCreate,
    DocumentSearchQuery,
    DocumentSearchResult,
    DocumentSearchResults,
    DocumentsList,
)
from rag_service.documents.tasks import index_document
from rag_service.exceptions.responses import (
    auth_responses,
    bad_request_response,
    internal_server_error_response,
    not_found_response,
    validation_error_response,
)
from rag_service.security.dependencies import AdminApiKeyDep

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get(
    path="",
    description="Get documents in the global knowledge base",
    responses={
        200: {
            "description": "Returns documents",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_documents(
    admin_id: AdminApiKeyDep,
    document_service: DocumentServiceDep,
) -> DocumentsList:
    document_models = await document_service.list_active()
    return DocumentsList(
        documents=[Document.model_validate(document_model) for document_model in document_models],
    )


@router.get(
    path="/{document_id}",
    description="Get a document by id",
    responses={
        200: {
            "description": "Returns a document",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def get_document(
    document_id: UUID,
    admin_id: AdminApiKeyDep,
    document_service: DocumentServiceDep,
) -> Document:
    document_model = await document_service.get_by_id_or_raise(document_id)
    return Document.model_validate(document_model)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    description="Create a document in the global knowledge base",
    responses={
        201: {
            "description": "Document has been created",
        },
        **auth_responses,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_document(
    document_create: DocumentCreate,
    background_tasks: BackgroundTasks,
    admin_id: AdminApiKeyDep,
    document_service: DocumentServiceDep,
) -> Document:
    document_model = await document_service.create_document(
        title=document_create.title,
        content=document_create.content,
        source=document_create.source,
        source_metadata=document_create.source_metadata,
    )
    background_tasks.add_task(index_document, document_model.id)
    return Document.model_validate(document_model)


@router.post(
    path="/search",
    description="Search document chunks in the global knowledge base",
    responses={
        200: {
            "description": "Returns matching document chunks",
        },
        **auth_responses,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def search_documents(
    search_query: DocumentSearchQuery,
    admin_id: AdminApiKeyDep,
    document_service: DocumentServiceDep,
) -> DocumentSearchResults:
    search_results = await document_service.search_documents(
        query=search_query.query,
        limit=search_query.limit,
    )
    return DocumentSearchResults(
        results=[
            DocumentSearchResult(
                score=result.score,
                document_id=UUID(result.document_id),
                chunk_id=UUID(result.chunk_id),
                chunk_index=result.chunk_index,
                content=result.content,
            )
            for result in search_results
        ],
    )


@router.post(
    path="/upload",
    status_code=status.HTTP_201_CREATED,
    description="Upload a file into the global knowledge base",
    responses={
        201: {
            "description": "Document has been uploaded",
        },
        **auth_responses,
        **bad_request_response,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def upload_document(
    file: Annotated[UploadFile, File(..., description="Upload file (.txt, .md, .docx, .pdf)")],
    background_tasks: BackgroundTasks,
    admin_id: AdminApiKeyDep,
    document_service: DocumentServiceDep,
) -> Document:
    extracted_document = await extract_document_from_upload(file)
    document_model = await document_service.create_document(
        title=extracted_document.title,
        content=extracted_document.content,
        source=extracted_document.source,
        source_metadata=extracted_document.source_metadata,
    )
    background_tasks.add_task(index_document, document_model.id)
    return Document.model_validate(document_model)


@router.delete(
    path="/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a document from the global knowledge base",
    responses={
        204: {
            "description": "Document has been deleted",
        },
        **auth_responses,
        **not_found_response,
        **internal_server_error_response,
    },
)
async def delete_document(
    document_id: UUID,
    admin_id: AdminApiKeyDep,
    document_service: DocumentServiceDep,
) -> None:
    await document_service.delete_document(document_id)
