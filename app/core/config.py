import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database Configuration
    POSTGRES_DB: str = "qflood"
    POSTGRES_USER: str = "dev"
    POSTGRES_PASSWORD: str = "dev"
    DATABASE_URL: str = "sqlite:///./qflood.db"

    # MinIO Configuration
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "qflood-data"
    MINIO_SECURE: bool = False # Default to False for local dev, but will be enforced for production

    # API Key Hashing Salt
    API_KEY_HASH_SALT: str = "dev-salt-change-in-production"

    # Redis Configuration (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Application Environment
    APP_ENV: str = "development" # 'development', 'testing', 'production'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enforce MINIO_SECURE=True for non-development/testing environments
        if self.APP_ENV not in ["development", "testing"]:
            if not self.MINIO_SECURE:
                logger.critical(
                    "SECURITY WARNING: MINIO_SECURE is False in a non-development/testing environment "
                    f"(APP_ENV={self.APP_ENV}). Forcing MINIO_SECURE to True. "
                    "Ensure proper TLS certificates are configured for MinIO."
                )
                self.MINIO_SECURE = True
            else:
                logger.info(f"MINIO_SECURE is True for APP_ENV={self.APP_ENV}, as required.")
        else:
            logger.info(f"MINIO_SECURE is {self.MINIO_SECURE} for APP_ENV={self.APP_ENV}.")


settings = Settings()
