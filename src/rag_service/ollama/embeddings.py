from ollama import AsyncClient

from rag_service.config import settings


class OllamaEmbeddingClient:
    """
    Ollama embeddings client.
    """

    def __init__(self):
        client_kwargs = {}
        if settings.OLLAMA_API_KEY:
            client_kwargs["headers"] = {"Authorization": f"Bearer {settings.OLLAMA_API_KEY}"}

        self.client = AsyncClient(
            host=settings.OLLAMA_BASE_URL,
            **client_kwargs,
        )
        self.model = settings.OLLAMA_EMBEDDING_MODEL

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Create embeddings for texts.
        """
        if not texts:
            return []

        response = await self.client.embed(
            model=self.model,
            input=texts,
            keep_alive="30m",
        )
        return [list(embedding) for embedding in response.embeddings]
