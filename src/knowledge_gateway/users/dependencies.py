from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from knowledge_gateway.database.config import sqlalchemy_config
from knowledge_gateway.users.services import UserService


async def provide_user_service() -> AsyncGenerator[UserService, None]:
    async with UserService.new(config=sqlalchemy_config) as service:
        yield service


type UserServiceDep = Annotated[UserService, Depends(provide_user_service)]
