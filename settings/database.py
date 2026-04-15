from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str

    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str | None = None
    COOKIE_MAX_AGE: int = 2592000  # 30 days