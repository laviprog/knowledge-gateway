import json
from typing import Any


def format_sse_event(data: dict[str, Any] | str) -> str:
    """
    Format data as a Server-Sent Event.
    """
    if isinstance(data, str):
        return f"data: {data}\n\n"

    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def build_chunk(
    completion_id: str,
    created: int,
    model: str,
    delta: dict[str, str],
    finish_reason: str | None = None,
) -> dict[str, Any]:
    """
    Build an OpenAI-compatible stream chunk.
    """
    return {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": delta,
                "finish_reason": finish_reason,
            }
        ],
    }


def build_usage_chunk(
    completion_id: str,
    created: int,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> dict[str, Any]:
    """
    Build an OpenAI-compatible usage stream chunk.
    """
    return {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }
