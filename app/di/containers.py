from dependency_injector import containers, providers

from app.di.repositories import RepositoriesContainer
from app.di.services import ServicesContainer
from settings.database import Settings


class DIContainer(containers.DeclarativeContainer):
    settings: Settings = providers.Singleton(Settings)

    repositories = providers.Container(
        RepositoriesContainer,
        settings=settings
    )

    services = providers.Container(
        ServicesContainer,
        settings=settings,
        repositories=repositories
    )
