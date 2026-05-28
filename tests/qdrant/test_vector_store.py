import asyncio

from rag_service.qdrant.vector_store import QdrantVectorStore


class FakeQdrantClient:
    def __init__(self, collection_exists: bool) -> None:
        self.collection_exists_result = collection_exists
        self.query_points_called = False

    async def collection_exists(self, collection_name: str) -> bool:
        return self.collection_exists_result

    async def query_points(self, **kwargs):
        self.query_points_called = True
        raise AssertionError("query_points should not be called")


def test_search_returns_empty_list_when_collection_does_not_exist() -> None:
    vector_store = object.__new__(QdrantVectorStore)
    vector_store.client = FakeQdrantClient(collection_exists=False)
    vector_store.collection_name = "documents"

    results = asyncio.run(vector_store.search(query_embedding=[0.1, 0.2], limit=5))

    assert results == []
    assert not vector_store.client.query_points_called
