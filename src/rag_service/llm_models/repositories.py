from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from rag_service.llm_models.models import LlmModel


class LlmModelRepository(SQLAlchemyAsyncRepository[LlmModel]):
    """LLM Model Repository"""

    model_type = LlmModel
