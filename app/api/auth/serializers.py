import re

from pydantic import BaseModel, Field, field_validator, EmailStr


class AuthUserSerializer(BaseModel):
    login: str = Field(
        ..., title="Логин пользователя", description="Уникальный логин для входа в систему", min_length=3
    )
    password: str = Field(
        ..., title="Пароль", description="Пароль для входа в систему", min_length=8
    )


class AuthUserResponseSerializer(BaseModel):
    session_token: str = Field(
        ..., max_length=100, title="ID сессии", description="Уникальный идентификатор сессии пользователя"
    )

    class Config:
        from_attributes = True


class AuthUserRegistrationSerializer(BaseModel):
    login: str = Field(..., title="Логин пользователя", description="Уникальный логин для регистрации")
    email: EmailStr = Field(..., title="Email", description="Email адрес пользователя")
    first_name: str = Field(..., title="Имя", description="Имя пользователя")
    last_name: str | None = Field(default=None, title="Фамилия", description="Фамилия пользователя")
    password: str = Field(..., title="Пароль", description="Пароль для регистрации")

    @field_validator("password")
    def password_complexity(cls, value: str) -> str:
        if not re.search(r"[a-zA-Z]", value) or not re.search(r"\d", value):
            raise ValueError("Пароль должен содержать хотя бы одну букву и одну цифру")
        if len(value) < 8:
            raise ValueError("Пароль должен быть не короче 8 символов")
        return value


class AuthUserRegistrationResponseSerializer(BaseModel):
    session_token: str = Field(
        ..., max_length=100, title="ID сессии", description="Уникальный идентификатор сессии пользователя"
    )
    login: str = Field(..., title="Логин пользователя", description="Уникальный логин для входа в систему")
    email: str = Field(..., title="Email", description="Email адрес пользователя")
    first_name: str = Field(..., title="Имя", description="Имя пользователя")
    last_name: str | None = Field(default=None, title="Фамилия", description="Фамилия пользователя")

    class Config:
        from_attributes = True

