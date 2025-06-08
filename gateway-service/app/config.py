from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    MEMBER_SERVICE_URL: str
    FEEDBACK_SERVICE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = {
        "extra": "ignore",  # This will ignore extra fields in the .env file
        "env_file": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    }

@lru_cache()
def get_settings():
    settings = Settings()
    return settings

settings = get_settings()