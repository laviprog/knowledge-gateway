import time
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from rag_service.config import settings
from rag_service.documents.models import DocumentChunkModel, DocumentIndexStatus, DocumentModel
from rag_service.documents.repositories import DocumentChunkRepository, DocumentRepository
from rag_service.documents.utils import hash_content, split_document_content
from rag_service.exceptions import NotFoundError
from rag_service.llm.embeddings import OpenAIEmbeddingClient
from rag_service.qdrant.schema import VectorSearchResult
from rag_service.qdrant.vector_store import QdrantVectorStore
from rag_service.utils import utc_now


@dataclass(frozen=True)
class DocumentSearchTimings:
    """
    Document search timings.
    """

    embedding_ms: float
    qdrant_search_ms: float
    total_ms: float


@dataclass(frozen=True)
class DocumentSearchWithMetrics:
    """
    Document search result with metrics.
    """

    results: list[VectorSearchResult]
    timings: DocumentSearchTimings


class DocumentService(SQLAlchemyAsyncRepositoryService[DocumentModel, DocumentRepository]):
    """Document Service"""

    repository_type = DocumentRepository

    def __init__(self, session, **kwargs):
        super().__init__(session=session, **kwargs)
        self.chunk_repository = DocumentChunkRepository(session=session)
        self.embedding_client = OpenAIEmbeddingClient()
        self.vector_store = QdrantVectorStore()

    async def list_active(self, limit: int, offset: int) -> tuple[list[DocumentModel], int]:
        """
        Return a page of documents that have not been soft-deleted, with the total count.
        """
        documents, total = await self.repository.list_and_count(
            DocumentModel.deleted_at.is_(None),
            LimitOffset(limit=limit, offset=offset),
            OrderBy(field_name="created_at", sort_order="desc"),
        )
        return list(documents), total

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
        search_result = await self.search_documents_with_metrics(query=query, limit=limit)
        return search_result.results

    async def search_documents_with_metrics(
        self,
        query: str,
        limit: int,
    ) -> DocumentSearchWithMetrics:
        """
        Search indexed document chunks and return timings.
        """
        total_start = time.perf_counter()

        embedding_start = time.perf_counter()
        embeddings = await self.embedding_client.embed_texts([query])
        embedding_ms = round((time.perf_counter() - embedding_start) * 1000, 2)

        qdrant_start = time.perf_counter()
        search_results = await self.vector_store.search(
            query_embedding=embeddings[0],
            limit=limit,
        )
        qdrant_search_ms = round((time.perf_counter() - qdrant_start) * 1000, 2)

        return DocumentSearchWithMetrics(
            results=search_results,
            timings=DocumentSearchTimings(
                embedding_ms=embedding_ms,
                qdrant_search_ms=qdrant_search_ms,
                total_ms=round((time.perf_counter() - total_start) * 1000, 2),
            ),
        )

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
