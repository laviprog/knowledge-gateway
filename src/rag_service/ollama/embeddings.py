from rag_service.config import settings
from rag_service.ollama.client import get_ollama_client


class OllamaEmbeddingClient:
    """
    Ollama embeddings client.
    """

    def __init__(self):
        self.client = get_ollama_client()
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
            keep_alive=settings.OLLAMA_KEEP_ALIVE,
        )
        return [list(embedding) for embedding in response.embeddings]
