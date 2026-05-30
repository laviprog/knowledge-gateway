from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from rag_service.documents.models import DocumentChunkModel, DocumentModel


class DocumentRepository(SQLAlchemyAsyncRepository[DocumentModel]):
    """Document Repository"""

    model_type = DocumentModel


class DocumentChunkRepository(SQLAlchemyAsyncRepository[DocumentChunkModel]):
    """Document Chunk Repository"""

    model_type = DocumentChunkModel
