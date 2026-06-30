from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from rag_service.knowledge_bases.models import KnowledgeBaseModel


class KnowledgeBaseRepository(SQLAlchemyAsyncRepository[KnowledgeBaseModel]):
    """Knowledge Base Repository"""

    model_type = KnowledgeBaseModel
