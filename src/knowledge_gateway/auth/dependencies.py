from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from knowledge_gateway.auth.services import AuthService
from knowledge_gateway.database.config import sqlalchemy_config
from knowledge_gateway.users.services import UserService


async def provide_auth_service() -> AsyncGenerator[AuthService, None]:
    async with UserService.new(config=sqlalchemy_config) as user_service:
        yield AuthService(user_service=user_service)


type AuthServiceDep = Annotated[AuthService, Depends(provide_auth_service)]
