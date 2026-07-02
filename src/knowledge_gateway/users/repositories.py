from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from knowledge_gateway.users.models import UserModel


class UserRepository(SQLAlchemyAsyncRepository[UserModel]):
    """User Repository"""

    model_type = UserModel
