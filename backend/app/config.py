"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """TraumaInsight application settings.

    Loads values from a .env file located in the project root
    (one level above backend/).
    """

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql://traumainsight:traumainsight_dev@localhost:5432/traumainsight"

    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # Testing
    TESTING: bool = False

    @property
    def async_database_url(self) -> str:
        """Convert the standard postgres URL to an async one for asyncpg."""
        return self.DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        )

    @property
    def sync_database_url(self) -> str:
        """Return the standard psycopg2 database URL."""
        if "postgresql://" in self.DATABASE_URL and "+asyncpg" not in self.DATABASE_URL:
            return self.DATABASE_URL
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
