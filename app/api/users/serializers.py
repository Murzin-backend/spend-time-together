from datetime import datetime

from pydantic import BaseModel, Field


class UserInfoSerializer(BaseModel):
    id: int = Field(title="ID пользователя")
    login: str = Field(title="Логин пользователя")
    email: str = Field(title="Email пользователя")
    first_name: str = Field(title="Имя пользователя")
    last_name: str | None = Field(title="Фамилия пользователя")
    avatar_url: str | None = Field(title="URL аватара")
    telegram_link: str | None = Field(title="Ссылка на Telegram", default=None)
    created_at: datetime = Field(title="Дата создания")
    updated_at: datetime = Field(title="Дата обновления")

    class Config:
        from_attributes = True


class UserUpdateSerializer(BaseModel):
    first_name: str | None = Field(None, title="Имя пользователя", min_length=1)
    last_name: str | None = Field(None, title="Фамилия пользователя", min_length=1)
    telegram_link: str | None = Field(None, title="Ссылка на Telegram", min_length=1)

    class Config:
        from_attributes = True
