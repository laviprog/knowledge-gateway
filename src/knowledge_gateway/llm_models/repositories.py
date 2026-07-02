from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from knowledge_gateway.llm_models.models import LlmModel


class LlmModelRepository(SQLAlchemyAsyncRepository[LlmModel]):
    """LLM Model Repository"""

    model_type = LlmModel
