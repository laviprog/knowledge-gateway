from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from knowledge_gateway.providers.models import ProviderModel


class ProviderRepository(SQLAlchemyAsyncRepository[ProviderModel]):
    """Provider Repository"""

    model_type = ProviderModel
