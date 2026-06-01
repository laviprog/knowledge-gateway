from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from rag_service.config import settings
from rag_service.ollama.client import get_ollama_client


class OllamaTimeoutError(Exception):
    """
    Raised when Ollama does not respond in time.
    """


@dataclass(frozen=True)
class OllamaChatChunk:
    """
    Ollama chat stream chunk.
    """

    content: str
    done: bool
    finish_reason: str | None
    prompt_tokens: int | None
    completion_tokens: int | None


class OllamaChatClient:
    """
    Ollama chat client.
    """

    def __init__(self):
        self.client = get_ollama_client()

    async def stream_chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        top_p: float | None = None,
        max_completion_tokens: int | None = None,
        think: bool | Literal["low", "medium", "high"] | None = False,
    ) -> AsyncIterator[OllamaChatChunk]:
        """
        Stream chat completion chunks.
        """
        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature

        if top_p is not None:
            options["top_p"] = top_p

        if max_completion_tokens is not None:
            options["num_predict"] = max_completion_tokens

        try:
            response = await self.client.chat(
                model=model,
                messages=messages,
                stream=True,
                options=options or None,
                keep_alive=settings.OLLAMA_KEEP_ALIVE,
                think=think,
            )

            async for chunk in response:
                yield OllamaChatChunk(
                    content=chunk.message.content or "",
                    done=bool(chunk.done),
                    finish_reason=chunk.done_reason,
                    prompt_tokens=chunk.prompt_eval_count,
                    completion_tokens=chunk.eval_count,
                )
        except httpx.TimeoutException as exc:
            raise OllamaTimeoutError("Ollama request timed out") from exc
