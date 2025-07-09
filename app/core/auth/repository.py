from dataclasses import dataclass

from sqlalchemy import select

from app.core.auth.models import UsersSession
from app.core.mixins import BaseRepository


@dataclass
class AuthRepository(BaseRepository):
    async def get_users_session(self, user_id: int) -> UsersSession | None:
        query = select(
            UsersSession
        ).where(UsersSession.user_id==user_id).order_by(UsersSession.created_at.desc()).limit(1)
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def save_user_session(self, user_id: int, session_token: str) -> UsersSession:
        new_session = UsersSession(user_id=user_id, session_token=session_token)
        async with self.db.session() as session:
            session.add(new_session)
            await session.commit()
            await session.refresh(new_session)
            return new_session