from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from knowledge_gateway.database.config import sqlalchemy_config
from knowledge_gateway.llm_models.services import LlmModelService


async def provide_llm_model_service() -> AsyncGenerator[LlmModelService, None]:
    async with LlmModelService.new(config=sqlalchemy_config) as service:
        yield service


type LlmModelServiceDep = Annotated[LlmModelService, Depends(provide_llm_model_service)]
