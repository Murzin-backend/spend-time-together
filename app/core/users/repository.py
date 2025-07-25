from dataclasses import dataclass

from sqlalchemy import select

from app.core.mixins import BaseRepository
from app.core.users.models import Users


@dataclass
class UserRepository(BaseRepository):
    async def get_users(self) -> list[Users]:
        query = select(Users)
        async with self.db.session() as session:
            result = await session.execute(query)
            return list(result.scalars().all())


    async def get_user_by_login(self, login: str) -> Users | None:
        query = select(Users).where(Users.login == login)
        async with self.db.session() as session:
            result = await session.execute(query)
            user = result.scalars().first()
            return user if user is not None else None


    async def get_user_by_email(self, email: str) -> Users | None:
        query = select(Users).where(Users.email == email)
        async with self.db.session() as session:
            result = await session.execute(query)
            user = result.scalars().first()
            return user if user is not None else None

    async def create_user(
        self,
        login: str,
        email: str,
        first_name: str,
        password: str,
        last_name: str | None = None,
    ) -> Users:
        new_user = Users(
            login=login,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        async with self.db.session() as session:
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user