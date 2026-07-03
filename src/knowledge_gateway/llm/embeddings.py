import time

from knowledge_gateway.llm.client import ProviderConfig, get_llm_client
from knowledge_gateway.log_config import get_log

log = get_log(__name__)


class OpenAIEmbeddingClient:
    """
    OpenAI-compatible embeddings client bound to a provider endpoint and a model.
    """

    def __init__(self, config: ProviderConfig, model: str):
        self.client = get_llm_client(config)
        self.model = model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Create embeddings for texts.
        """
        if not texts:
            return []

        started_at = time.perf_counter()
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        embeddings = [list(item.embedding) for item in response.data]

        log.debug(
            "Created embeddings",
            model=self.model,
            batch_size=len(texts),
            dimensions=len(embeddings[0]) if embeddings else 0,
            duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
        )
        return embeddings
