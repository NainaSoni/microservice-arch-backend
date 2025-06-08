from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        # Look for .env in parent directory
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

@lru_cache()
def get_settings():
    settings = Settings()
    logger.info("Member Service Settings:")
    logger.info(f"DATABASE_URL: {settings.DATABASE_URL}")
    logger.info(f"SECRET_KEY: {settings.SECRET_KEY}")  # Mask the secret key
    logger.info(f"ALGORITHM: {settings.ALGORITHM}")
    logger.info(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    return settings

settings = get_settings() 