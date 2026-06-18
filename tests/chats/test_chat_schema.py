from rag_service.chats.schema import ChatCompletionRequest


def test_chat_completion_request_ignores_unknown_fields() -> None:
    request = ChatCompletionRequest.model_validate(
        {
            "model": "rag-assistant-lite",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True,
            "stream_options": {"include_usage": True, "unknown": "ignored"},
            "think": "low",
            "metadata": {"trace_id": "test"},
            "tool_choice": "auto",
        }
    )

    assert request.model == "rag-assistant-lite"
    assert request.stream is True
    assert request.stream_options is not None
    assert request.stream_options.include_usage is True
    assert not hasattr(request, "think")
    assert not hasattr(request, "metadata")
