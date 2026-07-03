from uuid import uuid4

import pytest

from knowledge_gateway.chats.prompts import (
    build_rag_messages,
    get_latest_user_message,
    resolve_rag_instruction,
)
from knowledge_gateway.chats.schema import ChatMessage
from knowledge_gateway.config import settings
from knowledge_gateway.exceptions import BadRequestError
from knowledge_gateway.knowledge_bases.models import KnowledgeBaseModel
from knowledge_gateway.qdrant.schema import VectorSearchResult


def test_get_latest_user_message_returns_last_non_empty_user_message() -> None:
    messages = [
        ChatMessage(role="user", content="First question"),
        ChatMessage(role="assistant", content="First answer"),
        ChatMessage(role="user", content="Second question"),
    ]

    assert get_latest_user_message(messages) == "Second question"


def test_get_latest_user_message_requires_user_message() -> None:
    with pytest.raises(BadRequestError):
        get_latest_user_message([ChatMessage(role="assistant", content="Answer")])


def test_build_rag_messages_adds_context_to_system_message() -> None:
    messages = [
        ChatMessage(role="system", content="Be concise."),
        ChatMessage(role="user", content="How do returns work?"),
    ]
    chunks = [
        VectorSearchResult(
            score=0.9,
            document_id="document-id",
            chunk_id="chunk-id",
            chunk_index=0,
            content="Returns are available within 14 days.",
        )
    ]

    messages = build_rag_messages(messages, chunks)

    assert messages[0]["role"] == "system"
    assert "Be concise." in messages[0]["content"]
    assert "Returns are available within 14 days." in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "How do returns work?"}


def test_build_rag_messages_uses_global_instruction_by_default() -> None:
    messages = build_rag_messages(
        [ChatMessage(role="user", content="How do returns work?")],
        [],
    )

    assert settings.RAG_SYSTEM_INSTRUCTION in messages[0]["content"]


def test_build_rag_messages_accepts_custom_system_instruction() -> None:
    custom = "Answer strictly in German."

    messages = build_rag_messages(
        [ChatMessage(role="user", content="How do returns work?")],
        [],
        system_instruction=custom,
    )

    assert custom in messages[0]["content"]
    assert settings.RAG_SYSTEM_INSTRUCTION not in messages[0]["content"]


def _knowledge_base(system_prompt: str | None) -> KnowledgeBaseModel:
    return KnowledgeBaseModel(
        id=uuid4(),
        public_id="support",
        name="Support",
        embedding_model_id=uuid4(),
        system_prompt=system_prompt,
    )


def test_resolve_rag_instruction_falls_back_to_global_setting() -> None:
    assert resolve_rag_instruction(None) == settings.RAG_SYSTEM_INSTRUCTION
    assert resolve_rag_instruction(_knowledge_base(None)) == settings.RAG_SYSTEM_INSTRUCTION
    assert resolve_rag_instruction(_knowledge_base("")) == settings.RAG_SYSTEM_INSTRUCTION


def test_resolve_rag_instruction_prefers_knowledge_base_system_prompt() -> None:
    knowledge_base = _knowledge_base("You are the billing expert.")

    assert resolve_rag_instruction(knowledge_base) == "You are the billing expert."
