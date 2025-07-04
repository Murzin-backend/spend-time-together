from dataclasses import dataclass

from app.core.users.dto import UserDTO
from app.core.users.models import Users
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
                password=user.password,
                created_at=user.created_at,
                updated_at=user.updated_at
            ) for user in users
        ]
