import asyncio
from collections.abc import AsyncGenerator, AsyncIterator
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from uuid import uuid4

import pytest

from rag_service.chats.orchestrator import ChatCompletionError, ChatCompletionOrchestrator
from rag_service.chats.services import (
    ChatCompletionRequestLogService,
    ChatCompletionService,
    ChatCompletionTimeoutError,
)
from rag_service.exceptions import BadRequestError, NotFoundError
from rag_service.llm.base import ProviderTimeoutError

if TYPE_CHECKING:
    from rag_service.chats.schema import ChatCompletionRequest

_PLAN = SimpleNamespace(completion_id="chatcmpl-test")


class FakeRequestLogService:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.error_codes: list[str] = []
        self.request_log = SimpleNamespace(id=uuid4())

    async def create_pending(self, *, user_id, api_key_id, chat_request):
        self.calls.append("create_pending")
        return self.request_log

    async def mark_prepared(self, *, request_log, plan):
        self.calls.append("mark_prepared")
        return request_log

    async def finish_succeeded(self, *, request_log, plan, metrics):
        self.calls.append("finish_succeeded")
        return request_log

    async def finish_failed(
        self, *, request_log, error_code, error_message, plan=None, metrics=None
    ):
        self.calls.append("finish_failed")
        self.error_codes.append(error_code)
        return request_log

    async def finish_interrupted(self, *, request_log, plan):
        self.calls.append("finish_interrupted")
        return request_log


class FakeCompletionService:
    def __init__(
        self,
        *,
        prepare_exc: Exception | None = None,
        complete_result=None,
        complete_exc: Exception | None = None,
        stream_events: list[str] | None = None,
        stream_exc: Exception | None = None,
    ) -> None:
        self.prepare_exc = prepare_exc
        self.complete_result = complete_result
        self.complete_exc = complete_exc
        self.stream_events = stream_events or []
        self.stream_exc = stream_exc

    async def prepare_completion(self, chat_request):
        if self.prepare_exc is not None:
            raise self.prepare_exc
        return _PLAN

    async def complete(self, plan):
        if self.complete_exc is not None:
            raise self.complete_exc
        return self.complete_result

    async def stream_completion(
        self, plan, on_complete=None, on_timeout=None
    ) -> AsyncIterator[str]:
        if self.stream_exc is not None:
            raise self.stream_exc
        for event in self.stream_events:
            yield event
        if on_complete is not None:
            await on_complete(SimpleNamespace())


def build_orchestrator(
    completion_service: FakeCompletionService,
) -> tuple[ChatCompletionOrchestrator, FakeRequestLogService]:
    log_service = FakeRequestLogService()
    orchestrator = ChatCompletionOrchestrator(
        completion_service=cast("ChatCompletionService", completion_service),
        request_log_service=cast("ChatCompletionRequestLogService", log_service),
    )
    return orchestrator, log_service


async def _prepare(orchestrator: ChatCompletionOrchestrator):
    return await orchestrator.prepare(
        user_id=uuid4(),
        api_key_id=uuid4(),
        chat_request=cast("ChatCompletionRequest", SimpleNamespace()),
    )


def test_prepare_success_marks_pending_and_prepared() -> None:
    orchestrator, log_service = build_orchestrator(FakeCompletionService())

    result = asyncio.run(_prepare(orchestrator))

    assert result is _PLAN
    assert log_service.calls == ["create_pending", "mark_prepared"]


def test_prepare_maps_bad_request_to_400() -> None:
    orchestrator, log_service = build_orchestrator(
        FakeCompletionService(prepare_exc=BadRequestError("no user message"))
    )

    result = asyncio.run(_prepare(orchestrator))

    assert isinstance(result, ChatCompletionError)
    assert result.status_code == 400
    assert result.error_type == "invalid_request_error"
    assert log_service.calls == ["create_pending", "finish_failed"]


def test_prepare_maps_not_found_to_404() -> None:
    orchestrator, log_service = build_orchestrator(
        FakeCompletionService(prepare_exc=NotFoundError("Model not found"))
    )

    result = asyncio.run(_prepare(orchestrator))

    assert isinstance(result, ChatCompletionError)
    assert result.status_code == 404
    assert result.code == "model_not_found"
    assert log_service.error_codes == ["model_not_found"]


def test_prepare_maps_provider_timeout_to_503_and_finalizes_log() -> None:
    orchestrator, log_service = build_orchestrator(
        FakeCompletionService(prepare_exc=ProviderTimeoutError("LLM request timed out"))
    )

    result = asyncio.run(_prepare(orchestrator))

    assert isinstance(result, ChatCompletionError)
    assert result.status_code == 503
    assert result.code == "provider_timeout"
    assert log_service.calls == ["create_pending", "finish_failed"]


def test_prepare_finalizes_log_on_unexpected_error_and_reraises() -> None:
    orchestrator, log_service = build_orchestrator(
        FakeCompletionService(prepare_exc=RuntimeError("qdrant down"))
    )

    with pytest.raises(RuntimeError, match="qdrant down"):
        asyncio.run(_prepare(orchestrator))

    # Log row is finalized as FAILED rather than left PENDING.
    assert log_service.calls == ["create_pending", "finish_failed"]
    assert log_service.error_codes == ["preparation_failed"]


def test_complete_success_returns_response_and_finishes() -> None:
    response = SimpleNamespace(id="chatcmpl-test")
    completion_service = FakeCompletionService(
        complete_result=SimpleNamespace(response=response, metrics=SimpleNamespace())
    )
    orchestrator, log_service = build_orchestrator(completion_service)

    async def run():
        plan = await _prepare(orchestrator)
        return await orchestrator.complete(plan)

    result = asyncio.run(run())

    assert result is response
    assert "finish_succeeded" in log_service.calls


def test_complete_timeout_returns_503() -> None:
    completion_service = FakeCompletionService(
        complete_exc=ChatCompletionTimeoutError("LLM request timed out")
    )
    orchestrator, log_service = build_orchestrator(completion_service)

    async def run():
        plan = await _prepare(orchestrator)
        return await orchestrator.complete(plan)

    result = asyncio.run(run())

    assert isinstance(result, ChatCompletionError)
    assert result.status_code == 503
    assert result.code == "provider_timeout"
    assert log_service.error_codes == ["provider_timeout"]


def test_stream_success_invokes_completion_callback() -> None:
    completion_service = FakeCompletionService(stream_events=["data: a\n\n", "data: [DONE]\n\n"])
    orchestrator, log_service = build_orchestrator(completion_service)

    async def run() -> list[str]:
        plan = await _prepare(orchestrator)
        return [event async for event in orchestrator.stream(plan)]

    events = asyncio.run(run())

    assert events == ["data: a\n\n", "data: [DONE]\n\n"]
    assert "finish_succeeded" in log_service.calls


def test_stream_client_disconnect_marks_interrupted() -> None:
    completion_service = FakeCompletionService(stream_events=["data: a\n\n", "data: b\n\n"])
    orchestrator, log_service = build_orchestrator(completion_service)

    async def run() -> None:
        plan = await _prepare(orchestrator)
        stream = cast("AsyncGenerator[str, None]", orchestrator.stream(plan))
        await stream.__anext__()
        with pytest.raises(asyncio.CancelledError):
            await stream.athrow(asyncio.CancelledError())

    asyncio.run(run())

    assert "finish_interrupted" in log_service.calls
