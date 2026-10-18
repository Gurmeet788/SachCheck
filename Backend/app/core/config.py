import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "your-secret-key-here"
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/sachcheck_db"
    GOOGLE_FACT_CHECK_API_KEY: str = ""
    GOOGLE_FACT_CHECK_API_URL: str = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    FACT_CHECK_TIMEOUT_SECONDS: float = 10.0
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_API_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_TIMEOUT_SECONDS: float = 20.0
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_SIMILARITY_THRESHOLD: float = 0.85
    EMBEDDING_TIMEOUT_SECONDS: float = 10.0

    @property
    def sync_database_url(self) -> str:
        """
        Ensures the database connection URL is formatted for SQLAlchemy 2.x
        using the psycopg (v3) driver.
        """
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
