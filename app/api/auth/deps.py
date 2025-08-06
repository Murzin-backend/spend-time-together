from typing import Annotated
import logging
from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException, Request, status
from starlette.websockets import WebSocket

from app.core.auth.dto import UsersSessionDTO
from app.core.auth.service import AuthService
from app.di.containers import DIContainer

logger = logging.getLogger(__name__)


@inject
async def get_current_user_session(
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


async def get_authenticated_user_session(
    user_session_dto: Annotated[UsersSessionDTO | None, Depends(get_current_user_session)],
) -> UsersSessionDTO:
    """
    Проверяет, аутентифицирован ли пользователь.

    Если пользователь не аутентифицирован (равен None), вызывает исключение
    HTTP 401 Unauthorized. В противном случае возвращает объект пользователя.
    """
    if user_session_dto is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_session_dto


@inject
async def get_authenticated_user_for_ws(
    websocket: WebSocket,
    auth_service: AuthService = Depends(Provide[DIContainer.services.auth_service]),
) -> UsersSessionDTO | None:
    """
    Получает токен сессии из cookie WebSocket-соединения и возвращает пользователя.
    """
    try:
        session_token = websocket.cookies.get("session_token")
        if not session_token:
            logger.error("WebSocket аутентификация: session_token не найден в cookies")
            return None

        user_session_dto = await auth_service.get_user_session_by_token(session_token=session_token)
        if user_session_dto is None:
            logger.error(f"WebSocket аутентификация: недействительный токен {session_token}")
            return None

        logger.info(f"Успешная аутентификация пользователя {user_session_dto.user_id}")
        return user_session_dto
    except Exception as e:
        logger.error(f"Ошибка при аутентификации WebSocket: {str(e)}")
        return None
