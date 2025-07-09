from passlib.context import CryptContext


class PasswordService:
    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли обычный пароль хэшированному."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Возвращает хэш для пароля."""
        return self.pwd_context.hash(password)
