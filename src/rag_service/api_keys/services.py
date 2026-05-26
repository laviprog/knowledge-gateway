from datetime import datetime
from uuid import UUID

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import or_

from rag_service.api_keys.models import ApiKeyModel
from rag_service.api_keys.repositories import ApiKeyRepository
from rag_service.security.api_keys import generate_api_key_credentials, hash_api_key
from rag_service.utils import utc_now


class ApiKeyService(SQLAlchemyAsyncRepositoryService[ApiKeyModel, ApiKeyRepository]):
    """API key Service"""

    repository_type = ApiKeyRepository

    def __init__(self, session, **kwargs):
        super().__init__(session=session, **kwargs)

    async def create_api_key(
        self,
        user_id: UUID,
        name: str | None = None,
        expires_at: datetime | None = None,
        auto_commit: bool = True,
    ) -> tuple[ApiKeyModel, str]:

        api_key, api_key_prefix, api_key_hash = generate_api_key_credentials()

        api_key_model = await self.repository.add(
            ApiKeyModel(
                name=name,
                key_hash=api_key_hash,
                key_prefix=api_key_prefix,
                user_id=user_id,
                expires_at=expires_at,
            ),
            auto_commit=auto_commit,
        )

        return api_key_model, api_key

    async def validate_api_key(self, api_key: str) -> ApiKeyModel | None:
        """
        Validate the provided API key and return its ID if it is active.
        """
        key_hash = hash_api_key(api_key)

        api_key_model = await self.repository.get_one_or_none(
            *[
                ApiKeyModel.key_hash == key_hash,
                ApiKeyModel.deleted_at.is_(None),
                ApiKeyModel.revoked_at.is_(None),
                or_(
                    ApiKeyModel.expires_at.is_(None),
                    ApiKeyModel.expires_at > utc_now(),
                ),
            ]
        )

        if api_key_model:
            user_model = api_key_model.user
            if user_model.is_deleted:
                return None

            api_key_model = await self.repository.update_last_used_at(
                api_key_model,
                auto_commit=True,
            )
            return api_key_model

        return None
