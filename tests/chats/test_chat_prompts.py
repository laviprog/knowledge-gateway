import pytest

from rag_service.chats.prompts import build_rag_messages, get_latest_user_message
from rag_service.chats.schema import ChatMessage
from rag_service.exceptions import BadRequestError
from rag_service.qdrant.schema import VectorSearchResult


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

    ollama_messages = build_rag_messages(messages, chunks)

    assert ollama_messages[0]["role"] == "system"
    assert "Be concise." in ollama_messages[0]["content"]
    assert "Returns are available within 14 days." in ollama_messages[0]["content"]
    assert ollama_messages[1] == {"role": "user", "content": "How do returns work?"}
