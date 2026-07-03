from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from knowledge_gateway.chats.services import ChatCompletionRequestLogService
from knowledge_gateway.database.config import sqlalchemy_config


async def provide_chat_completion_request_log_service() -> AsyncGenerator[
    ChatCompletionRequestLogService, None
]:
    async with ChatCompletionRequestLogService.new(config=sqlalchemy_config) as service:
        yield service


type ChatCompletionRequestLogServiceDep = Annotated[
    ChatCompletionRequestLogService,
    Depends(provide_chat_completion_request_log_service),
]
