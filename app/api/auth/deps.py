from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException, Request, status, Query
from starlette.websockets import WebSocket

from app.core.auth.dto import UsersSessionDTO
from app.core.auth.service import AuthService
from app.di.containers import DIContainer


@inject
async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(Provide[DIContainer.services.auth_service]),
) -> UsersSessionDTO | None:
    """
    Получает токен сессии из cookie и возвращает пользователя.

    Если токен отсутствует или недействителен, возвращает None.
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None

    user_session_dto = await auth_service.get_user_session_by_token(session_token=session_token)
    return user_session_dto


async def get_authenticated_user(
    current_user: Annotated[UsersSessionDTO | None, Depends(get_current_user)],
) -> UsersSessionDTO:
    """
    Проверяет, аутентифицирован ли пользователь.

    Если пользователь не аутентифицирован (равен None), вызывает исключение
    HTTP 401 Unauthorized. В противном случае возвращает объект пользователя.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


@inject
async def get_authenticated_user_for_ws(
    websocket: WebSocket,
    token: str | None = Query(None),
    auth_service: AuthService = Depends(Provide[DIContainer.services.auth_service]),
) -> UsersSessionDTO | None:
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    user = await auth_service.get_user_session_by_token(token)
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    return user
