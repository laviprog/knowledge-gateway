from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol


class ProviderTimeoutError(Exception):
    """
    Raised when the LLM provider does not respond in time.
    """


@dataclass(frozen=True)
class ChatChunk:
    """
    Provider-agnostic chat stream chunk.
    """

    content: str
    finish_reason: str | None
    prompt_tokens: int | None
    completion_tokens: int | None


class ChatClient(Protocol):
    """
    Protocol for streaming chat clients, so providers can be swapped freely.
    """

    def stream_chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        top_p: float | None = None,
        max_completion_tokens: int | None = None,
    ) -> AsyncIterator[ChatChunk]: ...
