from fastapi import APIRouter, Cookie, Response, status

from rag_service.auth.cookies import clear_session_cookie, set_session_cookie
from rag_service.auth.dependencies import AuthServiceDep
from rag_service.auth.schema import LoginRequest, SessionUser
from rag_service.auth.session_store import create_session, delete_session
from rag_service.config import settings
from rag_service.exceptions.responses import (
    auth_responses,
    internal_server_error_response,
    validation_error_response,
)
from rag_service.security.dependencies import AdminSessionDep
from rag_service.users.dependencies import UserServiceDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    path="/login",
    description="Authenticate an admin and start a session",
    responses={
        200: {"description": "Session started; sets the session cookie"},
        **auth_responses,
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def login(
    login_request: LoginRequest,
    response: Response,
    auth_service: AuthServiceDep,
) -> SessionUser:
    user = await auth_service.authenticate(login_request.name, login_request.password)
    raw_token = await create_session(user.id)
    set_session_cookie(response, raw_token)
    return SessionUser.model_validate(user)


@router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    description="End the current session",
    responses={
        204: {"description": "Session ended; clears the session cookie"},
        **internal_server_error_response,
    },
)
async def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME),
) -> None:
    if session_token:
        await delete_session(session_token)
    clear_session_cookie(response)


@router.get(
    path="/me",
    description="Return the admin behind the current session",
    responses={
        200: {"description": "Returns the current admin"},
        **auth_responses,
        **internal_server_error_response,
    },
)
async def me(
    admin_context: AdminSessionDep,
    user_service: UserServiceDep,
) -> SessionUser:
    user = await user_service.get_by_id_or_raise(admin_context.user_id)
    return SessionUser.model_validate(user)
