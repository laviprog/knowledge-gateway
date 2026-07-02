from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from rag_service.auth import routes as auth_routes
from rag_service.auth.dependencies import provide_auth_service
from rag_service.config import settings
from rag_service.main import app
from rag_service.security.dependencies import AdminContext, require_admin_session
from rag_service.users.dependencies import provide_user_service
from rag_service.users.models import Role


def _admin(user_id=None) -> SimpleNamespace:
    return SimpleNamespace(id=user_id or uuid4(), name="admin", role=Role.ADMIN)


class FakeAuthService:
    def __init__(self, user: SimpleNamespace) -> None:
        self.user = user

    async def authenticate(self, name: str, password: str) -> SimpleNamespace:
        return self.user


@pytest.mark.anyio
async def test_login_sets_session_cookie(monkeypatch: pytest.MonkeyPatch) -> None:
    admin = _admin()
    monkeypatch.setattr(auth_routes, "create_session", lambda user_id: _async("raw-token"))
    app.dependency_overrides[provide_auth_service] = lambda: FakeAuthService(admin)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/login", json={"name": "admin", "password": "secret"}
            )
    finally:
        app.dependency_overrides.pop(provide_auth_service, None)

    assert response.status_code == 200
    assert response.json()["name"] == "admin"
    set_cookie = response.headers["set-cookie"]
    assert settings.SESSION_COOKIE_NAME in set_cookie
    assert "raw-token" in set_cookie
    assert "httponly" in set_cookie.lower()


@pytest.mark.anyio
async def test_logout_clears_cookie(monkeypatch: pytest.MonkeyPatch) -> None:
    deleted: list[str] = []
    monkeypatch.setattr(auth_routes, "delete_session", lambda token: _async(deleted.append(token)))

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies={settings.SESSION_COOKIE_NAME: "raw-token"},
    ) as client:
        response = await client.post("/auth/logout")

    assert response.status_code == 204
    assert deleted == ["raw-token"]
    assert "set-cookie" in response.headers


@pytest.mark.anyio
async def test_me_returns_current_admin() -> None:
    admin = _admin()

    class FakeUserService:
        async def get_by_id_or_raise(self, user_id) -> SimpleNamespace:
            return admin

    app.dependency_overrides[require_admin_session] = lambda: AdminContext(user_id=admin.id)
    app.dependency_overrides[provide_user_service] = lambda: FakeUserService()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/auth/me")
    finally:
        app.dependency_overrides.pop(require_admin_session, None)
        app.dependency_overrides.pop(provide_user_service, None)

    assert response.status_code == 200
    assert response.json()["id"] == str(admin.id)


async def _async(value):
    return value
