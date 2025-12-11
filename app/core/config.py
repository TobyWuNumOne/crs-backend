"""Application configuration (env-based). Use pydantic BaseSettings in a real implementation."""

from typing import Optional


class Settings:
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/crs"
    JWT_SECRET: str = "replace-this-with-secret"
    API_PREFIX: str = "/api/v1"


settings = Settings()
