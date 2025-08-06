from dataclasses import asdict

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Body, Depends, Response
from fastapi import status
from pydantic import BaseModel

from app.api.auth.deps import get_authenticated_user_session
from app.api.auth.exceptions import UserNotFoundException, UserAlreadyExistsException
from app.api.auth.serializers import AuthUserSerializer, AuthUserResponseSerializer, AuthUserRegistrationSerializer, \
    AuthUserRegistrationResponseSerializer
from app.api.response_patterns import OkResponse
from app.api.responses import build_responses
from app.api.routing import SpendTimeTogetherAPIRoute
from app.core.auth.dto import UsersSessionDTO
from app.core.auth.exceptions import UserNotFound, IncorrectPassword, UserAlreadyExists
from app.core.auth.service import AuthService
from app.di.containers import DIContainer

router = APIRouter(route_class=SpendTimeTogetherAPIRoute)

@router.post(
    "/auth/login",
    status_code=status.HTTP_200_OK,
    responses=build_responses(
        status_code=status.HTTP_200_OK,
        docs_response_model=OkResponse[AuthUserResponseSerializer],
        exceptions=(UserNotFoundException,),
    ),
    summary="Авторизация пользователя и выдача токена",
    response_model=OkResponse[AuthUserResponseSerializer],
)
@inject
async def login_user(
    response: Response,
    credentials: AuthUserSerializer = Body(),
    auth_service: AuthService = Depends(Provide[DIContainer.services.auth_service])
) -> OkResponse[AuthUserResponseSerializer]:
    """
    Авторизация пользователя и выдача токена.

    Этот эндпоинт позволяет пользователю войти в систему, предоставив свои учетные данные.
    В случае успешной авторизации возвращается токен доступа.
    """
    try:
        session_dto = await auth_service.authenticate_user(login=credentials.login, password=credentials.password)
    except (UserNotFound, IncorrectPassword) as error:
        raise UserNotFoundException(detail=str(error)) from error

    _set_cookie(
        response=response,
        session_token=session_dto.session_token,
    )

    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=AuthUserResponseSerializer,
        data={"session_token": session_dto.session_token}
    )


@router.post(
    "/auth/registration",
    status_code=status.HTTP_201_CREATED,
    responses=build_responses(
        status_code=status.HTTP_201_CREATED,
        docs_response_model=OkResponse[AuthUserRegistrationResponseSerializer],
        exceptions=(UserAlreadyExistsException,),
    ),
    summary="Регистрация пользователя и выдача токена",
    response_model=OkResponse[AuthUserRegistrationResponseSerializer],
)
@inject
async def user_registration(
    response: Response,
    registration_data: AuthUserRegistrationSerializer = Body(),
    auth_service: AuthService = Depends(Provide[DIContainer.services.auth_service])
) -> OkResponse[AuthUserRegistrationResponseSerializer]:
    """
    Регистрация пользователя и выдача токена.

    Этот эндпоинт позволяет пользователю зарегистрироваться в системе, предоставив свои учетные данные.
    В случае успешной регистрации возвращается токен доступа.
    """
    try:
        user_registration_dto = await auth_service.user_registration(
            login=registration_data.login,
            email=registration_data.email.__str__(),
            first_name=registration_data.first_name,
            last_name=registration_data.last_name,
            password=registration_data.password
        )
    except UserAlreadyExists as error:
        raise UserAlreadyExistsException(detail=str(error)) from error

    _set_cookie(
        response=response,
        session_token=user_registration_dto.session_token,
    )

    return OkResponse.new(
        status_code=status.HTTP_201_CREATED,
        model=AuthUserRegistrationResponseSerializer,
        data=asdict(user_registration_dto)
    )


@router.post(
    "/auth/logout",
    status_code=status.HTTP_200_OK,
    summary="Выход пользователя из системы",
    responses=build_responses(
        status_code=status.HTTP_200_OK,
        docs_response_model=OkResponse[BaseModel],
    ),
)
@inject
async def logout_user(
    response: Response,
    auth_service: AuthService = Depends(Provide[DIContainer.services.auth_service]),
    user_session: UsersSessionDTO = Depends(get_authenticated_user_session),
) -> OkResponse[BaseModel]:
    """
    Выход пользователя из системы.

    Этот эндпоинт позволяет пользователю выйти из системы, удаляя токен сессии.
    """
    await auth_service.logout_user(session_token=user_session.session_token)
    response.delete_cookie(key="session_token")
    return OkResponse.new(status_code=status.HTTP_200_OK, model=BaseModel, data={})

def _set_cookie(
    response: Response,
    session_token: str,
) -> None:
    """
    Устанавливает cookie с токеном сессии.

    :param response: Ответ FastAPI, в который будет добавлено cookie.
    :param session_token: Токен сессии для установки в cookie.
    """
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        samesite="lax",
    )
