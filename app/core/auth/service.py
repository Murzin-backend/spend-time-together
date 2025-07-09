import uuid
from dataclasses import dataclass

from app.core.auth.dto import UsersSessionDTO, UserRegistrationDTO
from app.core.auth.exceptions import UserNotFound, IncorrectPassword, UserAlreadyExists
from app.core.auth.password.password_service import PasswordService
from app.core.auth.repository import AuthRepository
from app.core.users.service import UserService
import asyncio


@dataclass
class AuthService:
    auth_repository: AuthRepository
    user_service: UserService
    password_service: PasswordService


    async def authenticate_user(self, login: str, password: str) -> UsersSessionDTO:
        user_dto = await self.user_service.get_user_by_login(login=login)

        if user_dto is None:
            raise UserNotFound(login=login)

        if not self.password_service.verify_password(
            plain_password=password, hashed_password=user_dto.password
        ):
            raise IncorrectPassword(login=login)

        return await self.get_or_create_user_session(user_id=user_dto.id)



    async def get_or_create_user_session(self, user_id: int) -> UsersSessionDTO:
        session = await self.auth_repository.get_users_session(user_id=user_id)
        if session is None:
            UUID = uuid.uuid4()
            session = await self.auth_repository.save_user_session(
                user_id=user_id, session_token=str(UUID)
            )
        return UsersSessionDTO(
            id=session.id,
            user_id=session.user_id,
            session_token=session.session_token,
            created_at=session.created_at,
            updated_at=session.updated_at
        )

    async def user_registration(
        self,
        login: str,
        password: str,
        first_name: str,
        last_name: str,
        email: str,
    ) -> UserRegistrationDTO:
        if await self._is_user_exist_by_login_or_email(login=login, email=email):
            raise UserAlreadyExists(login=login, email=email)

        hashed_password = self.password_service.get_password_hash(password=password)

        new_user = await self.user_service.create_user(
            login=login,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        session = await self.get_or_create_user_session(user_id=new_user.id)

        return UserRegistrationDTO(
            id=new_user.id,
            login=new_user.login,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            email=new_user.email,
            session_token=session.session_token,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )


    async def _is_user_exist_by_login_or_email(self, login: str, email: str) -> bool:
        user_by_login, user_by_email = await asyncio.gather(
            self.user_service.get_user_by_login(login=login),
            self.user_service.get_user_by_email(email=email),
        )
        return bool(user_by_login or user_by_email)







