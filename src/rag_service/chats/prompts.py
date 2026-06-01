from rag_service.config import settings
from rag_service.exceptions import BadRequestError
from rag_service.qdrant.schema import VectorSearchResult

from .schema import ChatMessage

RAG_SYSTEM_INSTRUCTION = """
Use the knowledge base context below to answer the user.
If the context does not contain enough information, say that the information is insufficient.
Keep the answer concise and suitable for a voice assistant.
""".strip()


def get_latest_user_message(messages: list[ChatMessage]) -> str:
    """
    Return the latest user message content.
    """
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content

    raise BadRequestError("At least one non-empty user message is required")


def build_rag_messages(
    messages: list[ChatMessage],
    context_chunks: list[VectorSearchResult],
) -> list[dict[str, str]]:
    """
    Build Ollama chat messages with RAG context.
    """
    system_content = build_system_content(messages, context_chunks)
    conversation_messages = [
        {"role": message.role, "content": message.content}
        for message in messages
        if message.role != "system"
    ]

    return [{"role": "system", "content": system_content}, *conversation_messages]


def build_system_content(
    messages: list[ChatMessage],
    context_chunks: list[VectorSearchResult],
) -> str:
    """
    Build system prompt content.
    """
    user_system_content = "\n\n".join(
        message.content for message in messages if message.role == "system" and message.content
    )
    context_content = format_context_chunks(context_chunks)

    sections = [
        section
        for section in [user_system_content, RAG_SYSTEM_INSTRUCTION, context_content]
        if section
    ]
    return "\n\n".join(sections)


def format_context_chunks(context_chunks: list[VectorSearchResult]) -> str:
    """
    Format retrieved chunks as prompt context.
    """
    if not context_chunks:
        return "Knowledge base context is empty."

    remaining_chars = settings.RAG_CONTEXT_MAX_CHARS
    formatted_chunks: list[str] = []

    for index, chunk in enumerate(context_chunks, start=1):
        content = chunk.content.strip()
        if not content:
            continue

        chunk_text = f"[{index}] {content}"
        if len(chunk_text) > remaining_chars:
            chunk_text = chunk_text[:remaining_chars].rstrip()

        formatted_chunks.append(chunk_text)
        remaining_chars -= len(chunk_text)
        if remaining_chars <= 0:
            break

    if not formatted_chunks:
        return "Knowledge base context is empty."

    return "Knowledge base context:\n" + "\n\n".join(formatted_chunks)
