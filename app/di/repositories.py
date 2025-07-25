from dependency_injector import containers, providers
from dependency_injector.providers import Singleton

from app.core.auth.repository import AuthRepository
from app.core.rooms.repository import RoomRepository
from app.core.users.repository import UserRepository
from app.infra.adapters.database import Database
from settings.database import Settings


class RepositoriesContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[Settings] = providers.Dependency()

    database = providers.Singleton(
        Database,
        db_url=settings.provided.DATABASE_URL,
    )

    user_repository: Singleton[UserRepository] = providers.Singleton(
        UserRepository,
        db=database
    )

    auth_repository: Singleton[AuthRepository] = providers.Singleton(
        AuthRepository,
        db=database
    )

    room_repository: Singleton = providers.Singleton(
        RoomRepository,
        db=database
    )
