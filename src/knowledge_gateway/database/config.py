from advanced_alchemy.extensions.fastapi import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)

from knowledge_gateway.config import settings

session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.DB_URL_ASYNC,
    session_config=session_config,
)
