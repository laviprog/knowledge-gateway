from typing import TYPE_CHECKING

from qdrant_client.models import Distance, PointIdsList, PointStruct, VectorParams

from rag_service.config import settings
from rag_service.documents.models import DocumentChunkModel
from rag_service.log_config import get_log
from rag_service.qdrant.client import get_qdrant_client
from rag_service.qdrant.schema import VectorSearchResult

if TYPE_CHECKING:
    from uuid import UUID

log = get_log(__name__)


class QdrantVectorStore:
    """
    Qdrant vector store.
    """

    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    async def ensure_collection(self, vector_size: int) -> None:
        """
        Create collection when it does not exist.
        """
        collection_exists = await self.client.collection_exists(self.collection_name)
        if collection_exists:
            return

        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        log.info(
            "Created Qdrant collection",
            collection=self.collection_name,
            vector_size=vector_size,
        )

    async def upsert_chunks(
        self,
        chunks: list[DocumentChunkModel],
        embeddings: list[list[float]],
    ) -> list[str]:
        """
        Upsert chunk embeddings into Qdrant.
        """
        if not chunks:
            return []

        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings count mismatch")

        await self.ensure_collection(vector_size=len(embeddings[0]))

        point_ids = [str(chunk.id) for chunk in chunks]
        points = [
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
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
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        log.debug(
            "Upserted points into Qdrant",
            collection=self.collection_name,
            points_count=len(point_ids),
        )

        return point_ids

    async def delete_points(self, point_ids: list[str]) -> None:
        """
        Delete points from Qdrant.
        """
        if not point_ids:
            return

        points: list[int | str | UUID] = [point_id for point_id in point_ids]
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=points),
            wait=True,
        )
        log.debug(
            "Deleted points from Qdrant",
            collection=self.collection_name,
            points_count=len(point_ids),
        )

    async def search(
        self,
        query_embedding: list[float],
        limit: int,
    ) -> list[VectorSearchResult]:
        """
        Search chunks by query embedding.
        """
        collection_exists = await self.client.collection_exists(self.collection_name)
        if not collection_exists:
            log.debug(
                "Qdrant search skipped: collection does not exist",
                collection=self.collection_name,
            )
            return []

        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
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
            collection=self.collection_name,
            limit=limit,
            results_count=len(results),
        )
        return results
