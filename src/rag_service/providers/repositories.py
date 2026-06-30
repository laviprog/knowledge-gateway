from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from rag_service.providers.models import ProviderModel


class ProviderRepository(SQLAlchemyAsyncRepository[ProviderModel]):
    """Provider Repository"""

    model_type = ProviderModel
