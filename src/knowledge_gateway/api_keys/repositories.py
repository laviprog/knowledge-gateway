from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from knowledge_gateway.api_keys.models import ApiKeyModel
from knowledge_gateway.utils import utc_now


class ApiKeyRepository(SQLAlchemyAsyncRepository[ApiKeyModel]):
    """API Key Repository"""

    model_type = ApiKeyModel

    async def update_last_used_at(self, api_key: ApiKeyModel, auto_commit: bool) -> ApiKeyModel:
        """
        Update last used at for an ApiKey model.
        """
        api_key.last_used_at = utc_now()
        return await self.update(api_key, auto_commit=auto_commit)
