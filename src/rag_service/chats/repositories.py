from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from rag_service.chats.models import ChatCompletionRequestLogModel


class ChatCompletionRequestLogRepository(SQLAlchemyAsyncRepository[ChatCompletionRequestLogModel]):
    """Chat Completion Request Log Repository"""

    model_type = ChatCompletionRequestLogModel
