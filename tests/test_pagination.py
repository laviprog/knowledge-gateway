from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from rag_service.main import app
from rag_service.pagination import DEFAULT_PAGE_LIMIT, PaginationParams
from rag_service.security.dependencies import AuthContext, require_admin
from rag_service.users.dependencies import provide_user_service

_USERS_URL = "/users"


def test_pagination_params_defaults() -> None:
    params = PaginationParams()
    assert params.limit == DEFAULT_PAGE_LIMIT
    assert params.offset == 0


class _RecordingUserService:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int]] = []

    async def list_active(self, limit: int, offset: int) -> tuple[list, int]:
        self.calls.append((limit, offset))
        return [], 7


@pytest.mark.anyio
async def test_get_users_forwards_pagination_and_returns_metadata() -> None:
    service = _RecordingUserService()
    auth = AuthContext(user_id=uuid4(), api_key_id=uuid4(), requests_per_minute=0)

    app.dependency_overrides[require_admin] = lambda: auth
    app.dependency_overrides[provide_user_service] = lambda: service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                _USERS_URL,
                params={"limit": 5, "offset": 10},
                headers={"Authorization": "Bearer dummy"},
            )
    finally:
        app.dependency_overrides.pop(require_admin, None)
        app.dependency_overrides.pop(provide_user_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body == {"users": [], "total": 7, "limit": 5, "offset": 10}
    assert service.calls == [(5, 10)]


@pytest.mark.anyio
async def test_get_users_uses_default_pagination_when_omitted() -> None:
    service = _RecordingUserService()
    auth = AuthContext(user_id=uuid4(), api_key_id=uuid4(), requests_per_minute=0)

    app.dependency_overrides[require_admin] = lambda: auth
    app.dependency_overrides[provide_user_service] = lambda: service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(_USERS_URL, headers={"Authorization": "Bearer dummy"})
    finally:
        app.dependency_overrides.pop(require_admin, None)
        app.dependency_overrides.pop(provide_user_service, None)

    assert response.status_code == 200
    assert service.calls == [(DEFAULT_PAGE_LIMIT, 0)]


@pytest.mark.anyio
@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"limit": -1},
        {"offset": -1},
    ],
)
async def test_get_users_rejects_out_of_range_pagination(params: dict[str, int]) -> None:
    auth = AuthContext(user_id=uuid4(), api_key_id=uuid4(), requests_per_minute=0)

    app.dependency_overrides[require_admin] = lambda: auth
    app.dependency_overrides[provide_user_service] = lambda: _RecordingUserService()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                _USERS_URL,
                params=params,
                headers={"Authorization": "Bearer dummy"},
            )
    finally:
        app.dependency_overrides.pop(require_admin, None)
        app.dependency_overrides.pop(provide_user_service, None)

    assert response.status_code == 422
