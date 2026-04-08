from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "IMEWS Backend"
    APP_ENV: str = "dev"
    APP_DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_PUBLIC_BASE_URL: str = "http://127.0.0.1:8000"

    TEACHER_INVITE_CODE: str = "IMEWS-TEACHER-2026"

    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "imews"
    MYSQL_ECHO: bool = False

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    JWT_SECRET_KEY: str = "change_this_to_a_long_random_string"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    SMS_MODE: str = "mock"   # mock / real
    SMS_CODE_EXPIRE_SECONDS: int = 300
    SMS_SEND_INTERVAL_SECONDS: int = 60
    FORGOT_PASSWORD_LIMIT_WINDOW_SECONDS: int = 600
    FORGOT_PASSWORD_LIMIT_MAX_ATTEMPTS: int = 5

    AI_ANALYSIS_WEBHOOK_URL: str = ""
    AI_CALLBACK_TOKEN: str = "imews-ai-callback-token"
    AI_REQUEST_TIMEOUT_SECONDS: int = 15

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
