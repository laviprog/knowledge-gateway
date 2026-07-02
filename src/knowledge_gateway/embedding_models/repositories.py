from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from knowledge_gateway.embedding_models.models import EmbeddingModel


class EmbeddingModelRepository(SQLAlchemyAsyncRepository[EmbeddingModel]):
    """Embedding Model Repository"""

    model_type = EmbeddingModel
