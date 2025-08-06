from dataclasses import asdict

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, UploadFile, File

from app.api.auth.deps import get_authenticated_user_session
from app.api.response_patterns import OkResponse
from app.api.responses import build_responses
from app.api.routing import SpendTimeTogetherAPIRoute
from app.api.users.exceptions import UserNotFoundException, UserConflictException, UserBadRequestException
from app.api.users.serializers import UserInfoSerializer, UserUpdateSerializer
from app.core.auth.dto import UsersSessionDTO
from app.core.users.dto import UserUpdateDTO
from app.core.users.exceptions import UserNotFound, LoginAlreadyExists, EmailAlreadyExists, AvatarException
from app.core.users.service import UserService
from app.di.containers import DIContainer

router = APIRouter(route_class=SpendTimeTogetherAPIRoute)


@router.get(
    "/users/me",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse[UserInfoSerializer],
    responses=build_responses(
        status_code=status.HTTP_200_OK,
        docs_response_model=OkResponse[UserInfoSerializer],
        exceptions=(UserNotFoundException,),
    ),
    summary="Получить информацию о текущем пользователе",
)
@inject
async def get_current_user_info(
    user_service: UserService = Depends(Provide[DIContainer.services.user_service]),
    user_session: UsersSessionDTO = Depends(get_authenticated_user_session),
) -> OkResponse[UserInfoSerializer]:
    try:
        user_dto = await user_service.get_user_by_id(user_id=user_session.user_id)
    except UserNotFound as error:
        raise UserNotFoundException(detail=str(error)) from error

    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=UserInfoSerializer,
        data=asdict(user_dto),
    )


@router.put(
    "/users/me",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse[UserInfoSerializer],
    responses=build_responses(
        status_code=status.HTTP_200_OK,
        docs_response_model=OkResponse[UserInfoSerializer],
        exceptions=(UserNotFoundException, UserConflictException),
    ),
    summary="Редактировать информацию о текущем пользователе",
)
@inject
async def update_current_user(
    update_data: UserUpdateSerializer,
    user_service: UserService = Depends(Provide[DIContainer.services.user_service]),
    user_session: UsersSessionDTO = Depends(get_authenticated_user_session),
) -> OkResponse[UserInfoSerializer]:
    update_dto = UserUpdateDTO(**update_data.model_dump(exclude_unset=True))
    try:
        updated_user_dto = await user_service.update_user(
            user_id=user_session.user_id, update_dto=update_dto
        )
    except UserNotFound as error:
        raise UserNotFoundException(detail=str(error)) from error
    except (LoginAlreadyExists, EmailAlreadyExists) as error:
        raise UserConflictException(detail=str(error)) from error

    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=UserInfoSerializer,
        data=asdict(updated_user_dto),
    )


@router.post(
    "/users/me/avatar",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse[UserInfoSerializer],
    responses=build_responses(
        status_code=status.HTTP_200_OK,
        docs_response_model=OkResponse[UserInfoSerializer],
        exceptions=(UserNotFoundException, UserBadRequestException),
    ),
    summary="Загрузить аватар для текущего пользователя",
)
@inject
async def upload_avatar(
    file: UploadFile = File(...),
    user_service: UserService = Depends(Provide[DIContainer.services.user_service]),
    user_session: UsersSessionDTO = Depends(get_authenticated_user_session),
) -> OkResponse[UserInfoSerializer]:
    try:
        updated_user_dto = await user_service.update_avatar(
            user_id=user_session.user_id, file=file
        )
    except UserNotFound as error:
        raise UserNotFoundException(detail=str(error)) from error
    except AvatarException as error:
        raise UserBadRequestException(detail=str(error)) from error

    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=UserInfoSerializer,
        data=asdict(updated_user_dto),
    )
