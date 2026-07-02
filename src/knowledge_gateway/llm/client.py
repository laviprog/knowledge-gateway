from dataclasses import dataclass

from openai import AsyncOpenAI


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


def get_llm_client(config: ProviderConfig) -> AsyncOpenAI:
    """
    Return a shared OpenAI-compatible client for the given provider config.
    """
    client = _clients.get(config)
    if client is None:
        client = AsyncOpenAI(
            base_url=config.base_url,
            # Some OpenAI-compatible servers require no key; the SDK still needs a non-empty value.
            api_key=config.api_key or "not-needed",
            timeout=config.timeout_seconds,
            # Retries transient errors (connection, 408/409/429, 5xx) with exponential backoff.
            max_retries=config.max_retries,
        )
        _clients[config] = client

    return client


async def close_llm_clients() -> None:
    """
    Close all cached OpenAI-compatible clients.
    """
    for client in _clients.values():
        await client.close()
    _clients.clear()
