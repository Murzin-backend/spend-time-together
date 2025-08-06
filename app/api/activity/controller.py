from dataclasses import asdict

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Path
from fastapi import status

from app.api.activity.serializers import ActivitySerializer, CreateActivitySerializer
from app.api.auth.deps import get_authenticated_user_session
from app.api.response_patterns import OkResponse
from app.api.responses import build_responses
from app.api.rooms.exceptions import RoomNotFoundException, UserNotInRoomException
from app.api.routing import SpendTimeTogetherAPIRoute
from app.core.activity.dto import CreateActivityDTO
from app.core.activity.service import ActivityService
from app.core.auth.dto import UsersSessionDTO
from app.core.rooms.exceptions import RoomNotFound, UserNotInRoom
from app.di.containers import DIContainer

router = APIRouter(route_class=SpendTimeTogetherAPIRoute)


@router.get(
    "/activities/{room_id}/all",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse[list[ActivitySerializer]],
    responses=build_responses(
        status_code=status.HTTP_200_OK,
        docs_response_model=OkResponse[list[ActivitySerializer]],
        exceptions=(
            RoomNotFoundException,
            UserNotInRoomException,
        ),
    ),
    summary="Получить все активности комнаты",
)
@inject
async def get_room_activities(
    room_id: int = Path(..., description="ID комнаты"),
    user_session: UsersSessionDTO = Depends(get_authenticated_user_session),
    activity_service: ActivityService = Depends(Provide[DIContainer.services.activity_service])
):
    try:
        activities_dto = await activity_service.get_activities_by_room_id(
            room_id=room_id,
            user_id=user_session.user_id
        )
    except RoomNotFound as error:
        raise RoomNotFoundException(detail=str(error)) from error
    except UserNotInRoom as error:
        raise UserNotInRoomException(detail=str(error)) from error

    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=list[ActivitySerializer],
        data=[asdict(activity) for activity in activities_dto],
    )


@router.post(
    "/activities/{room_id}/create",
    status_code=status.HTTP_201_CREATED,
    response_model=OkResponse[ActivitySerializer],
    responses=build_responses(
        status_code=status.HTTP_201_CREATED,
        docs_response_model=OkResponse[ActivitySerializer],
        exceptions=(
            RoomNotFoundException,
            UserNotInRoomException,
        ),
    ),
    summary="Создать быструю игру в комнате",
)
@inject
async def create_activity(
    activity_data: CreateActivitySerializer,
    room_id: int = Path(..., description="ID комнаты"),
    user_session: UsersSessionDTO = Depends(get_authenticated_user_session),
    activity_service: ActivityService = Depends(Provide[DIContainer.services.activity_service])
):
    try:
        activity_dto = await activity_service.create_activity(
            room_id=room_id,
            user_id=user_session.user_id,
            activity_dto=CreateActivityDTO(**activity_data.model_dump())
        )
    except RoomNotFound as error:
        raise RoomNotFoundException(detail=str(error)) from error
    except UserNotInRoom as error:
        raise UserNotInRoomException(detail=str(error)) from error

    return OkResponse.new(
        status_code=status.HTTP_201_CREATED,
        model=ActivitySerializer,
        data=asdict(activity_dto),
    )
