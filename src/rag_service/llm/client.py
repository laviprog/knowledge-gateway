from openai import AsyncOpenAI

from rag_service.config import settings

_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    """
    Return a shared OpenAI-compatible client.
    """
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.LLM_BASE_URL,
            # Some OpenAI-compatible servers require no key; the SDK still needs a non-empty value.
            api_key=settings.LLM_API_KEY or "not-needed",
            timeout=settings.LLM_TIMEOUT_SECONDS,
            # Retries transient errors (connection, 408/409/429, 5xx) with exponential backoff.
            max_retries=settings.LLM_MAX_RETRIES,
        )

    return _client


async def close_llm_client() -> None:
    """
    Close the shared OpenAI-compatible client.
    """
    global _client
    if _client is None:
        return

    await _client.close()
    _client = None
