from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Database:
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        echo: bool = False,
        pool_size: int = 5
    ) -> None:
        self._engine: AsyncEngine = create_async_engine(
            f"mysql+asyncmy://{user}:{password}@{host}/{database}",
            echo=echo,
            pool_size=pool_size,
            poolclass=AsyncAdaptedQueuePool,
            pool_pre_ping=True,
            pool_recycle=3600
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def disconnect(self) -> None:
        await self._engine.dispose()
