import asyncio
from types import SimpleNamespace

import pytest
from qdrant_client.models import Distance, VectorParams

from knowledge_gateway.qdrant.vector_store import QdrantVectorStore


class FakeQdrantClient:
    def __init__(self, collection_exists: bool, existing_size: int | None = None) -> None:
        self.collection_exists_result = collection_exists
        self.existing_size = existing_size
        self.query_points_called = False
        self.created_size: int | None = None

    async def collection_exists(self, collection_name: str) -> bool:
        return self.collection_exists_result

    async def get_collection(self, collection_name: str):
        vectors = VectorParams(size=self.existing_size or 0, distance=Distance.COSINE)
        return SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(vectors=vectors)))

    async def create_collection(self, collection_name: str, vectors_config: VectorParams) -> None:
        self.created_size = vectors_config.size

    async def create_payload_index(self, **kwargs) -> None:
        self.payload_index_field = kwargs.get("field_name")

    async def query_points(self, **kwargs):
        self.query_points_called = True
        raise AssertionError("query_points should not be called")


def _build_store(client: FakeQdrantClient) -> QdrantVectorStore:
    vector_store = object.__new__(QdrantVectorStore)
    vector_store.client = client
    return vector_store


def test_search_returns_empty_list_when_collection_does_not_exist() -> None:
    client = FakeQdrantClient(collection_exists=False)
    vector_store = _build_store(client)

    results = asyncio.run(
        vector_store.search(
            collection_name="documents",
            knowledge_base_id="kb-1",
            query_embedding=[0.1, 0.2],
            limit=5,
        )
    )

    assert results == []
    assert not client.query_points_called


class RecordingQdrantClient:
    """Fake client that records ``query_points`` kwargs and returns a single point."""

    def __init__(self) -> None:
        self.query_points_kwargs: dict | None = None

    async def collection_exists(self, collection_name: str) -> bool:
        return True

    async def query_points(self, **kwargs):
        self.query_points_kwargs = kwargs
        point = SimpleNamespace(
            score=0.9,
            payload={
                "document_id": "doc-1",
                "chunk_id": "chunk-1",
                "chunk_index": 0,
                "content": "Matching content",
            },
        )
        return SimpleNamespace(points=[point])


def test_search_forwards_score_threshold_to_query_points() -> None:
    client = RecordingQdrantClient()
    vector_store = object.__new__(QdrantVectorStore)
    vector_store.client = client

    results = asyncio.run(
        vector_store.search(
            collection_name="documents",
            knowledge_base_id="kb-1",
            query_embedding=[0.1, 0.2],
            limit=5,
            score_threshold=0.7,
        )
    )

    assert client.query_points_kwargs is not None
    assert client.query_points_kwargs["score_threshold"] == 0.7
    assert len(results) == 1
    assert results[0].content == "Matching content"


def test_search_defaults_score_threshold_to_none() -> None:
    client = RecordingQdrantClient()
    vector_store = object.__new__(QdrantVectorStore)
    vector_store.client = client

    asyncio.run(
        vector_store.search(
            collection_name="documents",
            knowledge_base_id="kb-1",
            query_embedding=[0.1, 0.2],
            limit=5,
        )
    )

    assert client.query_points_kwargs is not None
    assert client.query_points_kwargs["score_threshold"] is None


def test_ensure_collection_creates_when_missing() -> None:
    client = FakeQdrantClient(collection_exists=False)
    vector_store = _build_store(client)

    asyncio.run(vector_store.ensure_collection(collection_name="documents", vector_size=768))

    assert client.created_size == 768
    assert client.payload_index_field == "knowledge_base_id"


def test_ensure_collection_raises_on_dimension_mismatch() -> None:
    client = FakeQdrantClient(collection_exists=True, existing_size=768)
    vector_store = _build_store(client)

    with pytest.raises(ValueError, match="Embedding dimension mismatch"):
        asyncio.run(vector_store.ensure_collection(collection_name="documents", vector_size=1536))

    assert client.created_size is None


def test_ensure_collection_passes_on_matching_dimension() -> None:
    client = FakeQdrantClient(collection_exists=True, existing_size=768)
    vector_store = _build_store(client)

    asyncio.run(vector_store.ensure_collection(collection_name="documents", vector_size=768))

    assert client.created_size is None
