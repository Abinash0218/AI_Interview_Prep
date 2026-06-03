import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/interview_prep"
    SECRET_KEY: str = "change-me-in-production"
    JWT_SECRET: str = "change-jwt-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8501"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:8501"
    RESET_TOKEN_EXPIRE_MINUTES: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
