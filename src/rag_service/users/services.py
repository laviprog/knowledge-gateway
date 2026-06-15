from datetime import datetime
from uuid import UUID

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from rag_service.api_keys.models import ApiKeyModel
from rag_service.api_keys.services import ApiKeyService
from rag_service.exceptions import ConflictError, NotFoundError
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
        requests_per_minute: int = 60,
    ) -> UserModel:
        """
        Create a user.
        """
        return await self.repository.add(
            UserModel(
                name=name,
                role=role,
                requests_per_minute=requests_per_minute,
            ),
            auto_commit=True,
        )

    async def create_admin_with_api_key(
        self,
        name: str,
        api_key_name: str = "admin1",
        api_key_value: str | None = None,
    ) -> tuple[UserModel, str]:
        """
        Create an admin with an API key. Admins are unlimited (requests_per_minute=0).
        """
        admin = await self.repository.add(
            UserModel(
                name=name,
                role=Role.ADMIN,
                requests_per_minute=0,
            )
        )
        await self.repository.session.flush()

        _, api_key_value = await self.api_key_service.create_api_key(
            admin.id,
            name=api_key_name,
            api_key_value=api_key_value,
            auto_commit=False,
        )

        await self.repository.session.commit()

        return admin, api_key_value

    async def update_user(
        self,
        user_id: UUID,
        current_admin_id: UUID,
        name: str | None = None,
        role: Role | None = None,
        requests_per_minute: int | None = None,
    ) -> UserModel:
        """
        Update an active user.
        """
        user = await self.get_by_id_or_raise(user_id)

        if role is not None and user.id == current_admin_id and role != user.role:
            raise ConflictError("Admins cannot change their own role")

        if name is not None:
            user.name = name

        if role is not None:
            user.role = role

        if requests_per_minute is not None:
            user.requests_per_minute = requests_per_minute

        return await self.repository.update(user, auto_commit=True)

    async def delete_user(self, user_id: UUID, current_admin_id: UUID) -> None:
        """
        Soft-delete an active user and soft-delete their active API keys.
        """
        if user_id == current_admin_id:
            raise ConflictError("Admins cannot delete themselves")

        user = await self.get_by_id_or_raise(user_id)
        user.soft_delete()

        await self.repository.update(user, auto_commit=False)
        await self.api_key_service.delete_api_keys_for_user(user_id, auto_commit=False)
        await self.repository.session.commit()

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

    async def list_api_keys_for_user(self, user_id: UUID) -> list[ApiKeyModel]:
        """
        Return API keys for an existing active user.
        """
        user = await self.get_by_id_or_raise(user_id)
        return await self.api_key_service.list_for_user(user.id)

    async def get_by_id_or_raise(self, user_id: UUID) -> UserModel:
        """
        Return an active user or raise an exception if it does not exist.
        """
        user = await self.repository.get_one_or_none(
            UserModel.deleted_at.is_(None),
            id=user_id,
        )

        if user is None:
            raise NotFoundError()

        return user
