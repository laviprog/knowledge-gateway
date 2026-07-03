from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from knowledge_gateway.documents.models import DocumentChunkModel, DocumentModel


class DocumentRepository(SQLAlchemyAsyncRepository[DocumentModel]):
    """Document Repository"""

    model_type = DocumentModel


class DocumentChunkRepository(SQLAlchemyAsyncRepository[DocumentChunkModel]):
    """Document Chunk Repository"""

    model_type = DocumentChunkModel
