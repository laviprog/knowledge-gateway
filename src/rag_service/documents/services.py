from typing import Any
from uuid import UUID

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from rag_service.config import settings
from rag_service.documents.models import DocumentChunkModel, DocumentIndexStatus, DocumentModel
from rag_service.documents.repositories import DocumentChunkRepository, DocumentRepository
from rag_service.documents.utils import hash_content, split_document_content
from rag_service.exceptions import NotFoundError
from rag_service.ollama.embeddings import OllamaEmbeddingClient
from rag_service.qdrant.vector_store import QdrantVectorStore, VectorSearchResult
from rag_service.utils import utc_now


class DocumentService(SQLAlchemyAsyncRepositoryService[DocumentModel, DocumentRepository]):
    """Document Service"""

    repository_type = DocumentRepository

    def __init__(self, session, **kwargs):
        super().__init__(session=session, **kwargs)
        self.chunk_repository = DocumentChunkRepository(session=session)
        self.embedding_client = OllamaEmbeddingClient()
        self.vector_store = QdrantVectorStore()

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

    async def index_chunks(self, chunks: list[DocumentChunkModel]) -> None:
        """
        Index chunks in vector store.
        """
        if not chunks:
            return

        embeddings = await self.embedding_client.embed_texts([chunk.content for chunk in chunks])
        point_ids = await self.vector_store.upsert_chunks(chunks, embeddings)

        for chunk, point_id in zip(chunks, point_ids, strict=True):
            chunk.qdrant_point_id = point_id
            await self.chunk_repository.update(chunk, auto_commit=False)

    async def index_document(self, document_id: UUID) -> None:
        """
        Index a document in vector store.
        """
        document = await self.get_by_id_or_raise(document_id)
        document.index_status = DocumentIndexStatus.INDEXING
        document.index_error = None
        document.indexed_at = None
        await self.repository.update(document, auto_commit=True)

        try:
            chunks = await self.chunk_repository.list(
                DocumentChunkModel.document_id == document_id,
                DocumentChunkModel.deleted_at.is_(None),
            )
            await self.index_chunks(list(chunks))

            document.index_status = DocumentIndexStatus.INDEXED
            document.index_error = None
            document.indexed_at = utc_now()
            await self.repository.update(document, auto_commit=True)
        except Exception as exc:
            document.index_status = DocumentIndexStatus.FAILED
            document.index_error = str(exc)[:1000]
            document.indexed_at = None
            await self.repository.update(document, auto_commit=True)
            raise

    async def search_documents(self, query: str, limit: int) -> list[VectorSearchResult]:
        """
        Search indexed document chunks.
        """
        embeddings = await self.embedding_client.embed_texts([query])
        search_results = await self.vector_store.search(
            query_embedding=embeddings[0],
            limit=limit,
        )

        return search_results

    async def delete_document(self, document_id: UUID) -> None:
        """
        Soft-delete a document and its chunks.
        """
        document = await self.get_by_id_or_raise(document_id)
        document.soft_delete()

        chunks = await self.chunk_repository.list(
            DocumentChunkModel.document_id == document_id,
            DocumentChunkModel.deleted_at.is_(None),
        )
        qdrant_point_ids = [
            chunk.qdrant_point_id for chunk in chunks if chunk.qdrant_point_id is not None
        ]

        await self.vector_store.delete_points(qdrant_point_ids)
        await self.repository.update(document, auto_commit=False)

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
