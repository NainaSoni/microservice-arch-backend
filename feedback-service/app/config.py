from pydantic_settings import BaseSettings
from functools import lru_cache
import os

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
    return settings

settings = get_settings() 