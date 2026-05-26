from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from rag_service.database.config import sqlalchemy_config
from rag_service.users.services import UserService


async def provide_user_service() -> AsyncGenerator[UserService, None]:
    async with UserService.new(config=sqlalchemy_config) as service:
        yield service


type UserServiceDep = Annotated[UserService, Depends(provide_user_service)]
