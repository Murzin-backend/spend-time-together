import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.di.containers import DIContainer
from app.infra.adapters.database import Base
from app.main import create_app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Создает движок БД для тестов, который живет в течение всей сессии.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет сессию БД для одного теста, оборачивая его в транзакцию,
    которая откатывается после завершения теста.
    """
    async_session_maker = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def app(db_session: AsyncSession) -> AsyncGenerator[FastAPI, None]:
    """
    Создает экземпляр приложения для тестов с подмененной сессией БД.
    """
    mock_db = AsyncMock()
    mock_session_context = AsyncMock()
    mock_session_context.__aenter__.return_value = db_session
    mock_db.session = MagicMock(return_value=mock_session_context)

    test_container = DIContainer()
    test_container.repositories.database.override(mock_db)

    test_container.wire(
        modules=[
            "app.main",
            "app.api.users.controller",
        ],
        packages=["app.di"],
    )

    test_app = create_app(container=test_container)

    yield test_app

    test_container.unwire()


@pytest_asyncio.fixture()
async def rest_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app, base_url="http://test", headers={"Content-Type": "application/json"}
    ) as client:
        yield client