from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from app.api.response_patterns import OkResponse
from app.api.routing import SpendTimeTogetherAPIRoute
from app.api.users.serializers import UserInfoSerializer
from app.core.users.service import UserService
from app.di.containers import DIContainer
from dataclasses import asdict
router = APIRouter(route_class=SpendTimeTogetherAPIRoute)


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    response_model=OkResponse[list[UserInfoSerializer]],
    summary="Получить список пользователей",
)
@inject
async def get_users_list(
    user_service: UserService = Depends(Provide[DIContainer.services.user_service])
) -> OkResponse[list[UserInfoSerializer]]:
    users = await user_service.get_users()
    return OkResponse.new(
        status_code=status.HTTP_200_OK,
        model=list[UserInfoSerializer],
        data=[asdict(user) for user in users],
    )
