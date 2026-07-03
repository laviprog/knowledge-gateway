from typing import TYPE_CHECKING

from knowledge_gateway.config import settings
from knowledge_gateway.exceptions import BadRequestError
from knowledge_gateway.qdrant.schema import VectorSearchResult

from .schema import ChatMessage

if TYPE_CHECKING:
    from knowledge_gateway.knowledge_bases.models import KnowledgeBaseModel


def resolve_rag_instruction(knowledge_base: "KnowledgeBaseModel | None") -> str:
    """
    Resolve the RAG system instruction: a knowledge base's ``system_prompt`` overrides the
    global ``RAG_SYSTEM_INSTRUCTION`` setting.
    """
    if knowledge_base is not None and knowledge_base.system_prompt:
        return knowledge_base.system_prompt
    return settings.RAG_SYSTEM_INSTRUCTION


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
    system_instruction: str | None = None,
) -> list[dict[str, str]]:
    """
    Build chat messages with RAG context.
    """
    system_content = build_system_content(messages, context_chunks, system_instruction)
    conversation_messages = [
        {"role": message.role, "content": message.content}
        for message in messages
        if message.role != "system"
    ]

    return [{"role": "system", "content": system_content}, *conversation_messages]


def build_system_content(
    messages: list[ChatMessage],
    context_chunks: list[VectorSearchResult],
    system_instruction: str | None = None,
) -> str:
    """
    Build system prompt content.
    """
    instruction = (
        system_instruction if system_instruction is not None else settings.RAG_SYSTEM_INSTRUCTION
    )
    user_system_content = "\n\n".join(
        message.content for message in messages if message.role == "system" and message.content
    )
    context_content = format_context_chunks(context_chunks)

    sections = [
        section for section in [user_system_content, instruction, context_content] if section
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
