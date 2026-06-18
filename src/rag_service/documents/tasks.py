from uuid import UUID

from rag_service.database.config import sqlalchemy_config
from rag_service.documents.services import DocumentService
from rag_service.log_config import get_log

log = get_log(__name__)


async def index_document(document_id: UUID) -> None:
    """
    Index a document in the background.
    """
    log.info("Background document indexing task started", document_id=str(document_id))
    try:
        async with DocumentService.new(config=sqlalchemy_config) as service:
            await service.index_document(document_id)
    except Exception:
        log.exception("Background document indexing task failed", document_id=str(document_id))
