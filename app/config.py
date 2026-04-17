from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    API_ID: int
    API_HASH: str
    SESSION_PATH: str = "/data/session/account.session"
    SESSION_DIR: str = "/data/session"
    DATABASE_URL: str = "sqlite+aiosqlite:////data/database/media.db"
    DOWNLOAD_PATH: str = "/data/downloads"
    SYNC_INTERVAL: int = 600  # seconds
    MAX_PARALLEL_DOWNLOADS: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
