from dataclasses import dataclass

from sqlalchemy import select

from app.core.mixins import BaseRepository
from app.core.users.models import Users


@dataclass
class UserRepository(BaseRepository):
    async def get_users(self) -> list[Users]:
        query = select(Users)
        async with self.get_transaction_session() as session:
            result = await session.scalars(query)
            return list(result.all())
