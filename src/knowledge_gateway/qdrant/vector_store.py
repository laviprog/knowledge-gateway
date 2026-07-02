from typing import TYPE_CHECKING

from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PayloadSchemaType,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from knowledge_gateway.documents.models import DocumentChunkModel
from knowledge_gateway.log_config import get_log
from knowledge_gateway.qdrant.client import get_qdrant_client
from knowledge_gateway.qdrant.schema import VectorSearchResult

if TYPE_CHECKING:
    from uuid import UUID

log = get_log(__name__)

# Payload key used to isolate knowledge bases that share an embedding model's collection.
KNOWLEDGE_BASE_ID_FIELD = "knowledge_base_id"


class QdrantVectorStore:
    """
    Qdrant vector store. Operates on per-embedding-model collections; knowledge bases that
    share a collection are isolated by a ``knowledge_base_id`` payload filter.
    """

    def __init__(self):
        self.client = get_qdrant_client()

    async def ensure_collection(self, collection_name: str, vector_size: int) -> None:
        """
        Create the collection when it does not exist, or verify an existing one matches the
        embedding dimension.
        """
        collection_exists = await self.client.collection_exists(collection_name)
        if collection_exists:
            await self._assert_dimension(collection_name, vector_size)
            return

        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        # Indexed so per-knowledge-base filtering stays fast as the collection grows.
        await self.client.create_payload_index(
            collection_name=collection_name,
            field_name=KNOWLEDGE_BASE_ID_FIELD,
            field_schema=PayloadSchemaType.KEYWORD,
        )
        log.info(
            "Created Qdrant collection",
            collection=collection_name,
            vector_size=vector_size,
        )

    async def _assert_dimension(self, collection_name: str, vector_size: int) -> None:
        """
        Fail loudly when the existing collection's vector size differs from the embedding
        dimension (e.g. after pointing a knowledge base at a mismatched embedding model).
        """
        info = await self.client.get_collection(collection_name)
        vectors = info.config.params.vectors
        existing_size = vectors.size if isinstance(vectors, VectorParams) else None

        if existing_size is not None and existing_size != vector_size:
            raise ValueError(
                f"Embedding dimension mismatch: Qdrant collection "
                f"'{collection_name}' has vector size {existing_size}, but the configured "
                f"embedding model produces {vector_size}. Recreate the collection and "
                f"re-index documents after changing the embedding model."
            )

    async def upsert_chunks(
        self,
        collection_name: str,
        knowledge_base_id: str,
        chunks: list[DocumentChunkModel],
        embeddings: list[list[float]],
    ) -> list[str]:
        """
        Upsert chunk embeddings into the knowledge base's collection.
        """
        if not chunks:
            return []

        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings count mismatch")

        await self.ensure_collection(collection_name, vector_size=len(embeddings[0]))

        point_ids = [str(chunk.id) for chunk in chunks]
        points = [
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    KNOWLEDGE_BASE_ID_FIELD: knowledge_base_id,
                    "document_id": str(chunk.document_id),
                    "chunk_id": str(chunk.id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "content_hash": chunk.content_hash,
                },
            )
            for point_id, chunk, embedding in zip(point_ids, chunks, embeddings, strict=True)
        ]

        await self.client.upsert(
            collection_name=collection_name,
            points=points,
            wait=True,
        )
        log.debug(
            "Upserted points into Qdrant",
            collection=collection_name,
            knowledge_base_id=knowledge_base_id,
            points_count=len(point_ids),
        )

        return point_ids

    async def delete_points(self, collection_name: str, point_ids: list[str]) -> None:
        """
        Delete points from a collection.
        """
        if not point_ids:
            return

        points: list[int | str | UUID] = [point_id for point_id in point_ids]
        await self.client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=points),
            wait=True,
        )
        log.debug(
            "Deleted points from Qdrant",
            collection=collection_name,
            points_count=len(point_ids),
        )

    async def search(
        self,
        collection_name: str,
        knowledge_base_id: str,
        query_embedding: list[float],
        limit: int,
    ) -> list[VectorSearchResult]:
        """
        Search chunks within a single knowledge base by query embedding.
        """
        collection_exists = await self.client.collection_exists(collection_name)
        if not collection_exists:
            log.debug(
                "Qdrant search skipped: collection does not exist",
                collection=collection_name,
            )
            return []

        response = await self.client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key=KNOWLEDGE_BASE_ID_FIELD,
                        match=MatchValue(value=knowledge_base_id),
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        results: list[VectorSearchResult] = []
        for point in response.points:
            payload = point.payload or {}
            results.append(
                VectorSearchResult(
                    score=point.score,
                    document_id=str(payload["document_id"]),
                    chunk_id=str(payload["chunk_id"]),
                    chunk_index=int(payload["chunk_index"]),
                    content=str(payload["content"]),
                )
            )

        log.debug(
            "Qdrant search completed",
            collection=collection_name,
            knowledge_base_id=knowledge_base_id,
            limit=limit,
            results_count=len(results),
        )
        return results
