"""Application configuration (env-based). Use pydantic BaseSettings in a real implementation."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    DEVTEAM_PATH: str
    ENVIRONMENT: str
    PORT: int
    HOST: str
    RELOAD: bool
    WORKERS: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    # Base path for API routes (e.g. /api or /api/v1)
    API_PREFIX: str = "/api"

    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:

        return PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
