from dataclasses import dataclass

from openai import AsyncOpenAI

from rag_service.config import settings


@dataclass(frozen=True)
class ProviderConfig:
    """
    Connection settings for an OpenAI-compatible provider endpoint.
    """

    base_url: str
    api_key: str | None
    timeout_seconds: float
    max_retries: int


# Clients are reused per distinct connection config so a single endpoint shares one client
# (and its connection pool) across every model that points at it.
_clients: dict[ProviderConfig, AsyncOpenAI] = {}


def default_provider_config() -> ProviderConfig:
    """
    Provider config derived from environment settings (LLM_BASE_URL/LLM_API_KEY/...).

    Used for embeddings and as the fallback for LLM models with no provider record.
    """
    return ProviderConfig(
        base_url=settings.LLM_BASE_URL,
        api_key=settings.LLM_API_KEY,
        timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
        max_retries=settings.LLM_MAX_RETRIES,
    )


def get_llm_client(config: ProviderConfig | None = None) -> AsyncOpenAI:
    """
    Return a shared OpenAI-compatible client for the given provider config.

    Passing ``None`` resolves the environment-configured default provider.
    """
    resolved = config or default_provider_config()

    client = _clients.get(resolved)
    if client is None:
        client = AsyncOpenAI(
            base_url=resolved.base_url,
            # Some OpenAI-compatible servers require no key; the SDK still needs a non-empty value.
            api_key=resolved.api_key or "not-needed",
            timeout=resolved.timeout_seconds,
            # Retries transient errors (connection, 408/409/429, 5xx) with exponential backoff.
            max_retries=resolved.max_retries,
        )
        _clients[resolved] = client

    return client


async def close_llm_clients() -> None:
    """
    Close all cached OpenAI-compatible clients.
    """
    for client in _clients.values():
        await client.close()
    _clients.clear()
