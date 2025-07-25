from dependency_injector import containers, providers
from dependency_injector.providers import Singleton

from app.core.auth.password.password_service import PasswordService
from app.core.auth.service import AuthService
from app.core.rooms.service import RoomService
from app.core.users.service import UserService
from settings.database import Settings


class ServicesContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[Settings] = providers.Dependency()
    repositories = providers.DependenciesContainer()

    user_service: Singleton[UserService] = providers.Singleton(
        UserService,
        user_repository=repositories.user_repository
    )

    password_service: Singleton[PasswordService] = providers.Singleton(
        PasswordService
    )

    auth_service: Singleton[AuthService] = providers.Singleton(
        AuthService,
        user_service=user_service,
        password_service=password_service,
        auth_repository=repositories.auth_repository
    )

    room_service: Singleton = providers.Singleton(
        RoomService,
        room_repository=repositories.room_repository
    )