from dependency_injector import containers, providers
from dependency_injector.providers import Singleton

from settings.database import Settings
from app.core.users.repository import UserRepository
from app.infra.adapters.database import Database


class RepositoriesContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[Settings] = providers.Dependency()

    database = providers.Singleton(
        Database,
        host=settings.provided.MYSQL_HOST,
        user=settings.provided.MYSQL_USER,
        password=settings.provided.MYSQL_PASSWORD,
        database=settings.provided.MYSQL_DATABASE,
    )

    user_repository: Singleton[UserRepository] = providers.Singleton(
        UserRepository,
        db=database
    )
