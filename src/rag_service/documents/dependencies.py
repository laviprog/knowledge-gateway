from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from rag_service.database.config import sqlalchemy_config
from rag_service.documents.services import DocumentService


async def provide_document_service() -> AsyncGenerator[DocumentService, None]:
    async with DocumentService.new(config=sqlalchemy_config) as service:
        yield service


type DocumentServiceDep = Annotated[DocumentService, Depends(provide_document_service)]
