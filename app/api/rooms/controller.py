from dataclasses import asdict

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Path
from fastapi import status, Body

from app.api.auth.deps import get_authenticated_user
from app.api.response_patterns import OkResponse
from app.api.responses import build_responses
from app.api.rooms.exceptions import RoomNotFoundException, UserNotInRoomException, RoomNotFoundByInviteCodeException, \
    UserAlreadyInRoomException
from app.api.rooms.serializers import RoomInfoSerializer, RoomCreateSerializer, InviteCodeSerializer
from app.api.routing import SpendTimeTogetherAPIRoute
from app.core.rooms.exceptions import RoomNotFound, UserNotInRoom, RoomNotFoundByInviteCode, UserAlreadyInRoom
from app.core.rooms.service import RoomService
from app.core.users.dto import UserDTO
from app.di.containers import DIContainer

router = APIRouter(route_class=SpendTimeTogetherAPIRoute)


@router.get(
    "/rooms/all",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse[list[RoomInfoSerializer]],
    summary="Получить список комнат пользователя",
)
@inject
async def get_users_rooms_list(
    current_user: UserDTO = Depends(get_authenticated_user),
    room_service: RoomService = Depends(Provide[DIContainer.services.room_service])
) -> OkResponse[list[RoomInfoSerializer]]:
    """
    Получает список комнат пользователя.

    :param current_user: Аутентифицированный пользователь.
    :param room_service: Сервис для работы с комнатами.
    :return: Список комнат пользователя.
    """
    rooms = await room_service.get_rooms_by_user_id(current_user.id)
    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=list[RoomInfoSerializer],
        data=[asdict(room_dto) for room_dto in rooms],
    )


@router.post(
    "/rooms/create",
    status_code=status.HTTP_201_CREATED,
    response_model=OkResponse[RoomInfoSerializer],
    summary="Создать новую комнату",
)
@inject
async def create_room(
    current_user: UserDTO = Depends(get_authenticated_user),
    create_room_info: RoomCreateSerializer = Body(),
    room_service: RoomService = Depends(Provide[DIContainer.services.room_service])
) -> OkResponse[RoomInfoSerializer]:
    """
    Создает новую комнату.

    :param current_user: Аутентифицированный пользователь.
    :param room_service: Сервис для работы с комнатами.
    :return: Информация о созданной комнате.
    """
    room_dto = await room_service.create_room(
        user_id=current_user.id,
        name=create_room_info.name,
        description=create_room_info.description,
    )
    return OkResponse.new(
        status_code=status.HTTP_201_CREATED,
        model=RoomInfoSerializer,
        data=asdict(room_dto),
    )


@router.post(
    "/rooms/{room_id}/invite_code/create",
    status_code=status.HTTP_201_CREATED,
    response_model=OkResponse[InviteCodeSerializer],
    responses=build_responses(
        status_code=status.HTTP_201_CREATED,
        docs_response_model=OkResponse[InviteCodeSerializer],
        exceptions=(RoomNotFoundException,UserNotInRoomException),
    ),
    summary="Создать новую комнату",
)
@inject
async def create_invite_code(
    room_id: int = Path(..., description="ID комнаты"),
    current_user: UserDTO = Depends(get_authenticated_user),
    room_service: RoomService = Depends(Provide[DIContainer.services.room_service])
) -> OkResponse[InviteCodeSerializer]:
    """
    Создает код-приглашение для других юзеров в комнату

    :param room_id: id комнаты, для которой создается инвайт-код.
    :param current_user: Аутентифицированный пользователь.
    :param room_service: Сервис для работы с комнатами.
    :return: инвайт-код.
    """
    try:
        invite_code_dto = await room_service.create_invite_code(
            room_id=room_id,
            user_id=current_user.id,
        )
    except RoomNotFound as error:
        raise RoomNotFoundException(detail=str(error)) from error
    except UserNotInRoom as error:
        raise UserNotInRoomException(detail=str(error)) from error

    return OkResponse.new(
        status_code=status.HTTP_201_CREATED,
        model=InviteCodeSerializer,
        data=asdict(invite_code_dto),
    )


@router.post(
    "/rooms/invite_code/activate",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse[RoomInfoSerializer],
    responses=build_responses(
        status_code=status.HTTP_200_OK,
        docs_response_model=OkResponse[RoomInfoSerializer],
        exceptions=(RoomNotFoundException, RoomNotFoundByInviteCodeException, UserAlreadyInRoomException),
    ),
)
@inject
async def activate_invite_code(
    invite_code: str = Body(..., embed=True, description="Код-приглашение для комнаты"),
    current_user: UserDTO = Depends(get_authenticated_user),
    room_service: RoomService = Depends(Provide[DIContainer.services.room_service])
) -> OkResponse[RoomInfoSerializer]:
    """
    Активирует код-приглашение для комнаты.

    :param invite_code: Код-приглашение для комнаты.
    :param current_user: Аутентифицированный пользователь.
    :param room_service: Сервис для работы с комнатами.
    :return: Ответ об успешной активации кода.
    """
    try:
        room_dto = await room_service.activate_invite_code(
            invite_code=invite_code,
            user_id=current_user.id,
        )
    except RoomNotFound as error:
        raise RoomNotFoundException(detail=str(error)) from error
    except RoomNotFoundByInviteCode as error:
        raise RoomNotFoundByInviteCodeException(detail=str(error)) from error
    except UserAlreadyInRoom as error:
        raise UserAlreadyInRoomException(detail=str(error)) from error

    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=RoomInfoSerializer,
        data=asdict(room_dto)
    )
