from typing import Any
from uuid import UUID

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from rag_service.config import settings
from rag_service.documents.models import DocumentChunkModel, DocumentModel
from rag_service.documents.repositories import DocumentChunkRepository, DocumentRepository
from rag_service.documents.utils import hash_content, split_document_content
from rag_service.exceptions import NotFoundError


class DocumentService(SQLAlchemyAsyncRepositoryService[DocumentModel, DocumentRepository]):
    """Document Service"""

    repository_type = DocumentRepository

    def __init__(self, session, **kwargs):
        super().__init__(session=session, **kwargs)
        self.chunk_repository = DocumentChunkRepository(session=session)

    async def list_active(self) -> list[DocumentModel]:
        """
        Return documents that have not been soft-deleted.
        """
        documents = await self.repository.list(DocumentModel.deleted_at.is_(None))
        return list(documents)

    async def create_document(
        self,
        title: str,
        content: str,
        source: str | None = None,
        source_metadata: dict[str, Any] | None = None,
    ) -> DocumentModel:
        """
        Create a document in the global knowledge base.
        """
        document = await self.repository.add(
            DocumentModel(
                title=title,
                content=content,
                content_hash=hash_content(content),
                source=source,
                source_metadata=source_metadata or {},
            ),
            auto_commit=False,
        )
        await self.repository.session.flush()

        await self.create_chunks_for_document(document)
        await self.repository.session.commit()

        return document

    async def create_chunks_for_document(self, document: DocumentModel) -> list[DocumentChunkModel]:
        """
        Create chunks for a document.
        """
        chunk_contents = split_document_content(
            document.content,
            max_chars=settings.DOCUMENT_CHUNK_MAX_CHARS,
            overlap_chars=settings.DOCUMENT_CHUNK_OVERLAP_CHARS,
        )

        chunks: list[DocumentChunkModel] = []
        for index, chunk_content in enumerate(chunk_contents):
            chunk = await self.chunk_repository.add(
                DocumentChunkModel(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk_content,
                    content_hash=hash_content(chunk_content),
                ),
                auto_commit=False,
            )
            chunks.append(chunk)

        document.chunks = chunks
        return chunks

    async def delete_document(self, document_id: UUID) -> None:
        """
        Soft-delete a document and its chunks.
        """
        document = await self.get_by_id_or_raise(document_id)
        document.soft_delete()

        await self.repository.update(document, auto_commit=False)

        chunks = await self.chunk_repository.list(
            DocumentChunkModel.document_id == document_id,
            DocumentChunkModel.deleted_at.is_(None),
        )
        for chunk in chunks:
            chunk.soft_delete()
            await self.chunk_repository.update(chunk, auto_commit=False)

        await self.repository.session.commit()

    async def get_by_id_or_raise(self, document_id: UUID) -> DocumentModel:
        """
        Return an active document by id.
        """
        document = await self.repository.get_one_or_none(
            DocumentModel.deleted_at.is_(None),
            id=document_id,
        )

        if document is None:
            raise NotFoundError()

        return document
