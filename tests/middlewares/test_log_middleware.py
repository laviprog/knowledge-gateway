import pytest
import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

import rag_service.middlewares as middlewares_module
from rag_service.middlewares import LogMiddleware


def _make_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.add_middleware(LogMiddleware)

    @test_app.get("/ping")
    async def ping():
        return JSONResponse({"ok": True})

    return test_app


def _capture_bind(captured: dict):
    original = structlog.contextvars.bind_contextvars

    def capture(**kwargs):
        captured.update(kwargs)
        original(**kwargs)

    return capture


@pytest.mark.anyio
async def test_logs_direct_ip_when_proxy_is_not_trusted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(middlewares_module.settings, "TRUSTED_PROXY_IPS", [])
    captured: dict = {}
    monkeypatch.setattr(structlog.contextvars, "bind_contextvars", _capture_bind(captured))

    async with AsyncClient(
        transport=ASGITransport(app=_make_test_app()), base_url="http://test"
    ) as client:
        await client.get("/ping", headers={"X-Forwarded-For": "9.9.9.9"})

    assert captured.get("ip_address") != "9.9.9.9"


@pytest.mark.anyio
async def test_logs_forwarded_ip_when_proxy_is_trusted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(middlewares_module.settings, "TRUSTED_PROXY_IPS", ["127.0.0.1"])
    captured: dict = {}
    monkeypatch.setattr(structlog.contextvars, "bind_contextvars", _capture_bind(captured))

    async with AsyncClient(
        transport=ASGITransport(app=_make_test_app()), base_url="http://test"
    ) as client:
        await client.get("/ping", headers={"X-Forwarded-For": "1.2.3.4"})

    assert captured.get("ip_address") == "1.2.3.4"


@pytest.mark.anyio
async def test_logs_first_ip_from_x_forwarded_for(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(middlewares_module.settings, "TRUSTED_PROXY_IPS", ["127.0.0.1"])
    captured: dict = {}
    monkeypatch.setattr(structlog.contextvars, "bind_contextvars", _capture_bind(captured))

    async with AsyncClient(
        transport=ASGITransport(app=_make_test_app()), base_url="http://test"
    ) as client:
        await client.get("/ping", headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8, 9.9.9.9"})

    assert captured.get("ip_address") == "1.2.3.4"


@pytest.mark.anyio
async def test_sets_x_request_id_response_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(middlewares_module.settings, "TRUSTED_PROXY_IPS", [])

    async with AsyncClient(
        transport=ASGITransport(app=_make_test_app()), base_url="http://test"
    ) as client:
        response = await client.get("/ping")

    assert "x-request-id" in response.headers


@pytest.mark.anyio
async def test_echoes_incoming_x_request_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(middlewares_module.settings, "TRUSTED_PROXY_IPS", [])
    request_id = "test-correlation-id-123"

    async with AsyncClient(
        transport=ASGITransport(app=_make_test_app()), base_url="http://test"
    ) as client:
        response = await client.get("/ping", headers={"X-Request-Id": request_id})

    assert response.headers["x-request-id"] == request_id
