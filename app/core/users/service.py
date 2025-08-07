import logging
import os
import uuid
from dataclasses import dataclass

from PIL import Image
from fastapi import UploadFile

from app.core.users.constants import ALLOWED_AVATAR_CONTENT_TYPES, AVATAR_MAX_SIZE_MB, AVATAR_SIZE, AVATARS_DIR, \
    STATIC_ROOT
from app.core.users.dto import UserDTO, UserUpdateDTO
from app.core.users.exceptions import UserNotFound, AvatarTooLargeException, InvalidAvatarFormatException
from app.core.users.repository import UserRepository

logger = logging.getLogger(__name__)


@dataclass
class UserService:
    user_repository: UserRepository

    async def get_user_by_id(self, user_id: int) -> UserDTO | None:
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound(user_id=user_id)
        return UserDTO(
            id=user.id,
            login=user.login,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password=user.password,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

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
                updated_at=user.updated_at,
                avatar_url=user.avatar_url
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
            avatar_url=user.avatar_url,
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
            updated_at=user.updated_at,
            avatar_url=user.avatar_url
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
            updated_at=created_user.updated_at,
            avatar_url=created_user.avatar_url
        )

    async def update_user(self, user_id: int, update_dto: UserUpdateDTO) -> UserDTO:
        user = await self.user_repository.get_user_by_id(user_id=user_id)
        if not user:
            raise UserNotFound(user_id=user_id)

        update_data = update_dto.__dict__
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)

        updated_user = await self.user_repository.update_user(user=user)

        return UserDTO(
            id=updated_user.id,
            login=updated_user.login,
            email=updated_user.email,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            avatar_url=updated_user.avatar_url
        )

    async def update_avatar(self, user_id: int, file: UploadFile) -> UserDTO:
        if file.content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
            raise InvalidAvatarFormatException(
                detail=f"Only {', '.join(ALLOWED_AVATAR_CONTENT_TYPES)} formats are allowed."
            )

        file_bytes = await file.read()
        if len(file_bytes) > AVATAR_MAX_SIZE_MB * 1024 * 1024:
            raise AvatarTooLargeException(detail=f"Avatar size cannot exceed {AVATAR_MAX_SIZE_MB}MB.")

        await file.seek(0)
        image = Image.open(file.file)

        min_dim = min(image.width, image.height)
        left = (image.width - min_dim) / 2
        top = (image.height - min_dim) / 2
        right = (image.width + min_dim) / 2
        bottom = (image.height + min_dim) / 2
        image = image.crop((left, top, right, bottom))
        image = image.resize(AVATAR_SIZE)

        absolute_avatars_dir = os.path.join(STATIC_ROOT, AVATARS_DIR)

        os.makedirs(absolute_avatars_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4()}.png"
        absolute_file_path = os.path.join(absolute_avatars_dir, unique_filename)

        logger.info(f"Attempting to save avatar to: {absolute_file_path}")
        try:
            image.save(absolute_file_path, "PNG")
            logger.info(f"Successfully saved avatar to: {absolute_file_path}")
        except Exception as e:
            logger.error(f"Failed to save avatar to {absolute_file_path}. Error: {e}")
            raise

        avatar_url = f"/{AVATARS_DIR}/{unique_filename}"
        update_dto = UserUpdateDTO(avatar_url=avatar_url)

        return await self.update_user(user_id=user_id, update_dto=update_dto)

    async def get_users_by_ids(
        self,
        user_ids: list[int]
    ) -> list[UserDTO]:
        users = await self.user_repository.get_users_by_ids(user_ids)
        return [
            UserDTO(
                id=user.id,
                login=user.login,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                avatar_url=user.avatar_url
            ) for user in users
        ]
