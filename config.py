from pydantic_settings import BaseSettings
from functools import lru_cache
import secrets
from typing import List

class Settings(BaseSettings):
    
    PROJECT_NAME: str = "Slice API"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "API для магазина электроники Slice"

    DATABASE_URL: str = "postgresql://slice_user:simplepassword@localhost:5432/slice_db_new"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней

    # CORS_ORIGINS: str = "*"  # Заменяем List[str] на str
    # CORS_METHODS: str = "*"
    # CORS_HEADERS: str = "*"
    #
    # @property
    # def cors_origins_list(self):
    #     if self.CORS_ORIGINS == "*":
    #         return ["*"]
    #     return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()