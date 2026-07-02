import time
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from knowledge_gateway.config import settings
from knowledge_gateway.documents.models import (
    DocumentChunkModel,
    DocumentIndexStatus,
    DocumentModel,
)
from knowledge_gateway.documents.repositories import DocumentChunkRepository, DocumentRepository
from knowledge_gateway.documents.utils import hash_content, split_document_content
from knowledge_gateway.embedding_models.models import EmbeddingModel
from knowledge_gateway.exceptions import NotFoundError
from knowledge_gateway.knowledge_bases.models import KnowledgeBaseModel
from knowledge_gateway.knowledge_bases.repositories import KnowledgeBaseRepository
from knowledge_gateway.llm.embeddings import OpenAIEmbeddingClient
from knowledge_gateway.log_config import get_log
from knowledge_gateway.providers.config import resolve_provider_config
from knowledge_gateway.qdrant.schema import VectorSearchResult
from knowledge_gateway.qdrant.vector_store import QdrantVectorStore
from knowledge_gateway.utils import utc_now

log = get_log(__name__)


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
        self.knowledge_base_repository = KnowledgeBaseRepository(session=session)
        self.vector_store = QdrantVectorStore()

    @staticmethod
    def _embedding_client_for(embedding_model: EmbeddingModel) -> OpenAIEmbeddingClient:
        """
        Build an embedding client bound to the embedding model's provider and model name.
        """
        config = resolve_provider_config(embedding_model.inference_provider)
        return OpenAIEmbeddingClient(config, embedding_model.provider_model)

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
        knowledge_base_id: UUID,
        title: str,
        content: str,
        source: str | None = None,
        source_metadata: dict[str, Any] | None = None,
    ) -> DocumentModel:
        """
        Create a document in a knowledge base.
        """
        await self.ensure_knowledge_base_exists(knowledge_base_id)

        document = await self.repository.add(
            DocumentModel(
                knowledge_base_id=knowledge_base_id,
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

        log.info(
            "Document created",
            document_id=str(document.id),
            knowledge_base_id=str(knowledge_base_id),
            title=document.title,
            content_hash=document.content_hash,
            chunks_count=len(document.chunks),
            source=source,
        )
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

    async def index_chunks(
        self,
        knowledge_base: KnowledgeBaseModel,
        chunks: list[DocumentChunkModel],
    ) -> None:
        """
        Index chunks into the knowledge base's collection using its embedding model.
        """
        if not chunks:
            return

        embedding_model = knowledge_base.embedding_model
        embedding_client = self._embedding_client_for(embedding_model)

        embedding_start = time.perf_counter()
        embeddings = await embedding_client.embed_texts([chunk.content for chunk in chunks])
        embedding_ms = round((time.perf_counter() - embedding_start) * 1000, 2)

        upsert_start = time.perf_counter()
        point_ids = await self.vector_store.upsert_chunks(
            collection_name=embedding_model.collection_name,
            knowledge_base_id=str(knowledge_base.id),
            chunks=chunks,
            embeddings=embeddings,
        )
        upsert_ms = round((time.perf_counter() - upsert_start) * 1000, 2)

        for chunk, point_id in zip(chunks, point_ids, strict=True):
            chunk.qdrant_point_id = point_id
            await self.chunk_repository.update(chunk, auto_commit=False)

        log.debug(
            "Indexed chunks",
            knowledge_base_id=str(knowledge_base.id),
            collection=embedding_model.collection_name,
            chunks_count=len(chunks),
            embedding_ms=embedding_ms,
            upsert_ms=upsert_ms,
        )

    async def index_document(self, document_id: UUID) -> None:
        """
        Index a document in its knowledge base's vector store.
        """
        document = await self.get_by_id_or_raise(document_id)
        document.index_status = DocumentIndexStatus.INDEXING
        document.index_error = None
        document.indexed_at = None
        await self.repository.update(document, auto_commit=True)

        log.info("Document indexing started", document_id=str(document_id))
        started_at = time.perf_counter()

        try:
            chunks = await self.chunk_repository.list(
                DocumentChunkModel.document_id == document_id,
                DocumentChunkModel.deleted_at.is_(None),
            )
            await self.index_chunks(document.knowledge_base, list(chunks))

            document.index_status = DocumentIndexStatus.INDEXED
            document.index_error = None
            document.indexed_at = utc_now()
            await self.repository.update(document, auto_commit=True)

            log.info(
                "Document indexed",
                document_id=str(document_id),
                chunks_count=len(chunks),
                duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
            )
        except Exception as exc:
            document.index_status = DocumentIndexStatus.FAILED
            document.index_error = str(exc)[:1000]
            document.indexed_at = None
            await self.repository.update(document, auto_commit=True)

            log.warning(
                "Document indexing failed",
                document_id=str(document_id),
                error=str(exc)[:200],
                duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
            )
            raise

    async def search_documents(
        self,
        query: str,
        limit: int,
        knowledge_base: KnowledgeBaseModel | None,
    ) -> list[VectorSearchResult]:
        """
        Search indexed document chunks within a knowledge base.
        """
        search_result = await self.search_documents_with_metrics(
            query=query, limit=limit, knowledge_base=knowledge_base
        )
        return search_result.results

    async def search_documents_with_metrics(
        self,
        query: str,
        limit: int,
        knowledge_base: KnowledgeBaseModel | None,
    ) -> DocumentSearchWithMetrics:
        """
        Search indexed document chunks within a knowledge base and return timings.

        When no knowledge base is given (model without a knowledge base and no default),
        retrieval is skipped and an empty result is returned.
        """
        if knowledge_base is None:
            return DocumentSearchWithMetrics(
                results=[],
                timings=DocumentSearchTimings(embedding_ms=0.0, qdrant_search_ms=0.0, total_ms=0.0),
            )

        total_start = time.perf_counter()
        embedding_model = knowledge_base.embedding_model
        embedding_client = self._embedding_client_for(embedding_model)

        embedding_start = time.perf_counter()
        embeddings = await embedding_client.embed_texts([query])
        embedding_ms = round((time.perf_counter() - embedding_start) * 1000, 2)

        qdrant_start = time.perf_counter()
        search_results = await self.vector_store.search(
            collection_name=embedding_model.collection_name,
            knowledge_base_id=str(knowledge_base.id),
            query_embedding=embeddings[0],
            limit=limit,
        )
        qdrant_search_ms = round((time.perf_counter() - qdrant_start) * 1000, 2)

        timings = DocumentSearchTimings(
            embedding_ms=embedding_ms,
            qdrant_search_ms=qdrant_search_ms,
            total_ms=round((time.perf_counter() - total_start) * 1000, 2),
        )

        log.debug(
            "Document search completed",
            knowledge_base_id=str(knowledge_base.id),
            collection=embedding_model.collection_name,
            query_length=len(query),
            limit=limit,
            results_count=len(search_results),
            embedding_ms=timings.embedding_ms,
            qdrant_search_ms=timings.qdrant_search_ms,
            total_ms=timings.total_ms,
        )

        return DocumentSearchWithMetrics(results=search_results, timings=timings)

    async def delete_document(self, document_id: UUID) -> None:
        """
        Soft-delete a document and its chunks, removing its vectors from the collection.
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

        collection_name = document.knowledge_base.embedding_model.collection_name
        await self.vector_store.delete_points(collection_name, qdrant_point_ids)
        await self.repository.update(document, auto_commit=False)

        for chunk in chunks:
            chunk.soft_delete()
            await self.chunk_repository.update(chunk, auto_commit=False)

        await self.repository.session.commit()

        log.info(
            "Document deleted",
            document_id=str(document_id),
            knowledge_base_id=str(document.knowledge_base_id),
            chunks_count=len(chunks),
            qdrant_points_removed=len(qdrant_point_ids),
        )

    async def delete_documents_for_knowledge_base(self, knowledge_base: KnowledgeBaseModel) -> int:
        """
        Soft-delete every active document (and its chunks) in a knowledge base and remove their
        vectors from the collection. Returns the number of documents removed.
        """
        documents = await self.repository.list(
            DocumentModel.knowledge_base_id == knowledge_base.id,
            DocumentModel.deleted_at.is_(None),
        )
        if not documents:
            return 0

        collection_name = knowledge_base.embedding_model.collection_name
        qdrant_point_ids: list[str] = []

        for document in documents:
            chunks = await self.chunk_repository.list(
                DocumentChunkModel.document_id == document.id,
                DocumentChunkModel.deleted_at.is_(None),
            )
            for chunk in chunks:
                if chunk.qdrant_point_id is not None:
                    qdrant_point_ids.append(chunk.qdrant_point_id)
                chunk.soft_delete()
                await self.chunk_repository.update(chunk, auto_commit=False)

            document.soft_delete()
            await self.repository.update(document, auto_commit=False)

        await self.vector_store.delete_points(collection_name, qdrant_point_ids)
        await self.repository.session.commit()

        log.info(
            "Knowledge base documents deleted",
            knowledge_base_id=str(knowledge_base.id),
            documents_count=len(documents),
            qdrant_points_removed=len(qdrant_point_ids),
        )
        return len(documents)

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

    async def ensure_knowledge_base_exists(self, knowledge_base_id: UUID) -> None:
        """
        Ensure the referenced knowledge base exists and is active.
        """
        knowledge_base = await self.knowledge_base_repository.get_one_or_none(
            KnowledgeBaseModel.deleted_at.is_(None),
            id=knowledge_base_id,
        )
        if knowledge_base is None:
            raise NotFoundError("Knowledge base not found")
