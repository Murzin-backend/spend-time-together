from datetime import datetime

from pydantic import BaseModel, Field


class UserInfoSerializer(BaseModel):
    id: int = Field(title="ID пользователя")
    login: str = Field(title="Логин пользователя")
    email: str = Field(title="Email пользователя")
    first_name: str = Field(title="Имя пользователя")
    last_name: str = Field(title="Фамилия пользователя")
    created_at: datetime = Field(title="Дата создания")
    updated_at: datetime = Field(title="Дата обновления")

    class Config:
        from_attributes = True
