from typing import Optional
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tidal Helper"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tidal_helper.db")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_to_random_string")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Tidal
    TIDAL_API_TOKEN: Optional[str] = os.getenv("TIDAL_API_TOKEN")
    TIDAL_CLIENT_ID: Optional[str] = os.getenv("TIDAL_CLIENT_ID")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
