# backend/src/core/settings.py
import os
from functools import lru_cache
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    # Load settings from .env, but allow .env.test to override if ENVIRONMENT=test
    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("ENVIRONMENT") == "test" else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "The Churninator"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    INFERENCE_SERVER_URL: str = "http://inference:8001/predict"
    VLM_PROVIDER: Literal["local", "openai", "huggingface"] = "local"
    OPENAI_API_KEY: str | None = None
    HF_INFERENCE_API_KEY: str | None = None
    HF_MODEL_ID: str | None = None

    # --- Security & JWT ---
    # Generate a good secret key with: openssl rand -hex 32
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Connection Pooling
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_MAX_OVERFLOW: int = 5
    POSTGRES_POOL_TIMEOUT: int = 30
    POSTGRES_POOL_RECYCLE: int = 1800
    POSTGRES_USE_SSL: bool = True

    DATABASE_URL: PostgresDsn

    # --- Redis / Dramatiq ---
    REDIS_HOST: str
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self) -> RedisDsn:
        return RedisDsn(f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}")

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]  # For local Next.js dev


@lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of the settings."""
    return Settings()
