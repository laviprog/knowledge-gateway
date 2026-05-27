from datetime import datetime
from uuid import UUID

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import or_

from rag_service.api_keys.models import ApiKeyModel
from rag_service.api_keys.repositories import ApiKeyRepository
from rag_service.exceptions import ConflictError, NotFoundError
from rag_service.security.api_keys import (
    generate_api_key_credentials,
    get_api_key_credentials,
    hash_api_key,
)
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
        api_key_value: str | None = None,
        auto_commit: bool = True,
    ) -> tuple[ApiKeyModel, str]:
        if api_key_value:
            api_key, api_key_prefix, api_key_hash = get_api_key_credentials(api_key_value)
        else:
            api_key, api_key_prefix, api_key_hash = generate_api_key_credentials()

        existing_api_key = await self.repository.get_one_or_none(
            ApiKeyModel.key_hash == api_key_hash,
        )
        if existing_api_key is not None:
            raise ConflictError("API key already exists")

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

    async def list_for_user(self, user_id: UUID) -> list[ApiKeyModel]:
        """
        Return non-deleted API keys for the given user.
        """
        api_keys = await self.repository.list(
            ApiKeyModel.user_id == user_id,
            ApiKeyModel.deleted_at.is_(None),
        )
        return list(api_keys)

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

    async def delete_api_keys_for_user(
        self,
        user_id: UUID,
        auto_commit: bool = True,
    ) -> None:
        """
        Delete all API keys for the given user.
        """
        api_keys = await self.repository.list(
            ApiKeyModel.user_id == user_id,
        )

        for api_key in api_keys:
            api_key.soft_delete()
            await self.repository.update(api_key, auto_commit=False)

        if auto_commit:
            await self.repository.session.commit()

    async def revoke(self, api_key_id: UUID) -> ApiKeyModel:
        """
        Revoke an API key.
        """
        api_key_model = await self.repository.get_one_or_none(
            ApiKeyModel.id == api_key_id,
            ApiKeyModel.deleted_at.is_(None),
        )

        if api_key_model is None:
            raise NotFoundError()

        if api_key_model.revoked_at is None:
            api_key_model.revoked_at = utc_now()
            api_key_model = await self.repository.update(api_key_model, auto_commit=True)

        return api_key_model
