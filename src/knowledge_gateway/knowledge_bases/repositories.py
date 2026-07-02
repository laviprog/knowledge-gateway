from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from knowledge_gateway.knowledge_bases.models import KnowledgeBaseModel


class KnowledgeBaseRepository(SQLAlchemyAsyncRepository[KnowledgeBaseModel]):
    """Knowledge Base Repository"""

    model_type = KnowledgeBaseModel
