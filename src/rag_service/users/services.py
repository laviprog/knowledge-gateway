from datetime import datetime
from uuid import UUID

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from rag_service.api_keys.models import ApiKeyModel
from rag_service.api_keys.services import ApiKeyService
from rag_service.exceptions import NotFoundError
from rag_service.users.models import Role, UserModel
from rag_service.users.repositories import UserRepository


class UserService(SQLAlchemyAsyncRepositoryService[UserModel, UserRepository]):
    """User Service"""

    repository_type = UserRepository

    def __init__(self, session, **kwargs):
        super().__init__(session=session, **kwargs)
        self.api_key_service = ApiKeyService(session=session)

    async def list_active(self) -> list[UserModel]:
        """
        Return users that have not been soft-deleted.
        """
        users = await self.repository.list(UserModel.deleted_at.is_(None))
        return list(users)

    async def create_user(
        self,
        name: str,
        role: Role = Role.USER,
    ) -> UserModel:
        """
        Create a user.
        """
        return await self.repository.add(
            UserModel(
                name=name,
                role=role,
            ),
            auto_commit=True,
        )

    async def create_admin_with_api_key(self, name: str) -> tuple[UserModel, str]:
        """
        Create an admin with an API key.
        """
        admin = await self.repository.add(
            UserModel(
                name=name,
                role=Role.ADMIN,
            )
        )
        await self.repository.session.flush()

        _, api_key_value = await self.api_key_service.create_api_key(
            admin.id,
            "admin1",
            auto_commit=False,
        )

        await self.repository.session.commit()

        return admin, api_key_value

    async def create_api_key_for_user(
        self,
        user_id: UUID,
        name: str | None = None,
        expires_at: datetime | None = None,
    ) -> tuple[ApiKeyModel, str]:
        """
        Create an API key for an existing active user.
        """
        user_model = await self.repository.get_one_or_none(id=user_id)
        if user_model is None or user_model.is_deleted:
            raise NotFoundError()

        api_key_model, api_key_value = await self.api_key_service.create_api_key(
            user_id,
            name=name,
            expires_at=expires_at,
        )

        return api_key_model, api_key_value

    async def get_by_id_or_raise(self, user_id: UUID) -> UserModel:
        user = await self.repository.get_one_or_none(
            UserModel.deleted_at.is_(None),
            id=user_id,
        )

        if user is None:
            raise NotFoundError()

        return user
