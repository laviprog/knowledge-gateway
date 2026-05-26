from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from rag_service.users.models import UserModel


class UserRepository(SQLAlchemyAsyncRepository[UserModel]):
    """User Repository"""

    model_type = UserModel
