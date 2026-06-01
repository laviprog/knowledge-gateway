from typing import Any

from ollama import AsyncClient
from rag_service.config import settings

_client: AsyncClient | None = None


def get_ollama_client() -> AsyncClient:
    """
    Return a shared Ollama client.
    """
    global _client
    if _client is None:
        client_kwargs: dict[str, Any] = {"timeout": settings.OLLAMA_TIMEOUT_SECONDS}
        if settings.OLLAMA_API_KEY:
            client_kwargs["headers"] = {"Authorization": f"Bearer {settings.OLLAMA_API_KEY}"}

        _client = AsyncClient(
            host=settings.OLLAMA_BASE_URL,
            **client_kwargs,
        )

    return _client


async def close_ollama_client() -> None:
    """
    Close the shared Ollama client.
    """
    global _client
    if _client is None:
        return

    await _client.close()
    _client = None
