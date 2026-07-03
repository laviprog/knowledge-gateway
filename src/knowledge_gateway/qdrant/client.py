from qdrant_client import AsyncQdrantClient

from knowledge_gateway.config import settings

_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    """
    Return a shared Qdrant client.
    """
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )

    return _client


async def close_qdrant_client() -> None:
    """
    Close the shared Qdrant client.
    """
    global _client
    if _client is None:
        return

    await _client.close()
    _client = None
