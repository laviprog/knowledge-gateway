from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, cast

import openai

from rag_service.llm.base import ChatChunk, ProviderTimeoutError
from rag_service.llm.client import get_llm_client

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam


class OpenAIChatClient:
    """
    OpenAI-compatible chat client.
    """

    def __init__(self):
        self.client = get_llm_client()

    async def stream_chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        top_p: float | None = None,
        max_completion_tokens: int | None = None,
    ) -> AsyncIterator[ChatChunk]:
        """
        Stream chat completion chunks.
        """
        params: dict[str, Any] = {}
        if temperature is not None:
            params["temperature"] = temperature

        if top_p is not None:
            params["top_p"] = top_p

        if max_completion_tokens is not None:
            params["max_completion_tokens"] = max_completion_tokens

        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=cast("list[ChatCompletionMessageParam]", messages),
                stream=True,
                # Ask the provider to emit a final usage chunk; ignored gracefully if unsupported.
                stream_options={"include_usage": True},
                **params,
            )

            async for chunk in stream:
                content = ""
                finish_reason = None
                if chunk.choices:
                    choice = chunk.choices[0]
                    content = choice.delta.content or ""
                    finish_reason = choice.finish_reason

                prompt_tokens = None
                completion_tokens = None
                if chunk.usage is not None:
                    prompt_tokens = chunk.usage.prompt_tokens
                    completion_tokens = chunk.usage.completion_tokens

                yield ChatChunk(
                    content=content,
                    finish_reason=finish_reason,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )
        except openai.APITimeoutError as exc:
            raise ProviderTimeoutError("LLM request timed out") from exc
