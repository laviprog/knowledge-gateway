import asyncio
from types import SimpleNamespace

from rag_service.llm.client import ProviderConfig
from rag_service.llm.embeddings import OpenAIEmbeddingClient

_TEST_CONFIG = ProviderConfig(
    base_url="http://example",
    api_key=None,
    timeout_seconds=30,
    max_retries=2,
)


class FakeEmbeddings:
    def __init__(self, vectors: list[list[float]]) -> None:
        self._vectors = vectors
        self.kwargs: dict | None = None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(data=[SimpleNamespace(embedding=vector) for vector in self._vectors])


def build_client(vectors: list[list[float]]) -> tuple[OpenAIEmbeddingClient, FakeEmbeddings]:
    client = OpenAIEmbeddingClient(_TEST_CONFIG, "bge-m3")
    embeddings = FakeEmbeddings(vectors)
    client.client = SimpleNamespace(embeddings=embeddings)  # ty: ignore[invalid-assignment]
    return client, embeddings


def test_embed_texts_returns_empty_for_no_input() -> None:
    client, embeddings = build_client([])

    result = asyncio.run(client.embed_texts([]))

    assert result == []
    # The provider is not called for empty input.
    assert embeddings.kwargs is None


def test_embed_texts_maps_response_data_and_forwards_model() -> None:
    client, embeddings = build_client([[0.1, 0.2], [0.3, 0.4]])

    result = asyncio.run(client.embed_texts(["a", "b"]))

    assert result == [[0.1, 0.2], [0.3, 0.4]]
    assert embeddings.kwargs is not None
    assert embeddings.kwargs["input"] == ["a", "b"]
    assert embeddings.kwargs["model"] == client.model
