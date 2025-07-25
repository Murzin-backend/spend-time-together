from dataclasses import dataclass

from app.core.users.dto import UserDTO
from app.core.users.repository import UserRepository


@dataclass
class UserService:
    user_repository: UserRepository

    async def get_users(self) -> list[UserDTO]:
        users = await self.user_repository.get_users()
        return [
            UserDTO(
                id=user.id,
                login=user.login,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=user.created_at,
                updated_at=user.updated_at
            ) for user in users
        ]

    async def get_user_by_login(self, login: str) -> UserDTO | None:
        user = await self.user_repository.get_user_by_login(login)
        if user is None:
            return None
        return UserDTO(
            id=user.id,
            login=user.login,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def get_user_by_email(self, email: str) -> UserDTO | None:
        user = await self.user_repository.get_user_by_email(email)
        if user is None:
            return None
        return UserDTO(
            id=user.id,
            login=user.login,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


    async def create_user(
        self,
        login: str,
        email: str,
        first_name: str,
        hashed_password: str,
        last_name: str | None = None,
    ):
        created_user = await self.user_repository.create_user(
            login=login,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password
        )

        return UserDTO(
            id=created_user.id,
            login=created_user.login,
            email=created_user.email,
            first_name=created_user.first_name,
            last_name=created_user.last_name,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
        )
