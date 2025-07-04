from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.adapters.database import Database


@dataclass
class BaseRepository:
    db: Database

    @asynccontextmanager
    async def get_transaction_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.db.session() as session:
            try:
                yield session
            except Exception as error:
                await session.rollback()
                raise error
            else:
                await session.commit()

    @asynccontextmanager
    async def session_wrap(self, session: AsyncSession | None) -> AsyncGenerator[AsyncSession, None]:
        if session is not None:
            yield session
        else:
            async with self.db.session() as wrapped_session:
                yield wrapped_session
                await wrapped_session.commit()