from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.routes import api_router
from app.di.containers import DIContainer


@asynccontextmanager
async def lifespan(app: FastAPI, container: DIContainer) -> AsyncGenerator[None, None]:
    """
    Контекстный менеджер для управления жизненным циклом приложения.
    Выполняет wire и shutdown для контейнера DI.
    """
    container.wire(
        modules=[
            "app.main",
            "app.api.users.controller",
        ],
        packages=["app.di"],
    )
    yield
    container.unwire()


def create_app(container: DIContainer | None = None) -> FastAPI:
    """
    Фабрика для создания экземпляра приложения FastAPI.
    Может принимать предварительно сконфигурированный контейнер DI.
    """
    if container is None:
        container = DIContainer()

    app_lifespan = partial(lifespan, container=container)

    app = FastAPI(
        title="Spend Time Together",
        description="Backend API for Spend Time Together application",
        version="0.1.0",
        lifespan=app_lifespan
    )

    app.container = container
    app.include_router(api_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)