from dependency_injector import containers, providers
from dependency_injector.providers import Singleton

from app.core.users.service import UserService
from settings.database import Settings


class ServicesContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[Settings] = providers.Dependency()
    repositories = providers.DependenciesContainer()

    user_service: Singleton[UserService] = providers.Singleton(
        UserService,
        user_repository=repositories.user_repository
    )