import json

from knowledge_gateway.chats.sse import build_chunk, format_sse_event


def test_format_sse_event_formats_json_data() -> None:
    event = format_sse_event(
        build_chunk(
            completion_id="chatcmpl-1",
            created=1,
            model="rag-assistant-lite",
            delta={"content": "Hello"},
        )
    )

    assert event.startswith("data: ")
    assert event.endswith("\n\n")
    payload = json.loads(event.removeprefix("data: ").strip())
    assert payload["choices"][0]["delta"]["content"] == "Hello"


def test_format_sse_event_formats_done_marker() -> None:
    assert format_sse_event("[DONE]") == "data: [DONE]\n\n"
