# app/api/auth/deps.py
from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException, Request, status

from app.core.auth.service import AuthService
from app.core.users.dto import UserDTO
from app.di.containers import DIContainer


@inject
async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(Provide[DIContainer.services.auth_service]),
) -> UserDTO | None:
    """
    Получает токен сессии из cookie и возвращает пользователя.

    Если токен отсутствует или недействителен, возвращает None.
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None

    user = await auth_service.get_user_by_session_token(session_token)
    return user


async def get_authenticated_user(
    current_user: Annotated[UserDTO | None, Depends(get_current_user)],
) -> UserDTO:
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