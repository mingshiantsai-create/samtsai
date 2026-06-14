from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/blood_pressure.db"
    )

    # API
    api_title: str = "❤️ 血壓監測應用 API"
    api_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS
    allowed_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost",
        "http://127.0.0.1",
        "*"  # Docker 環境允許所有來源
    ]

    # Data scraping
    update_schedule_hour: int = 18  # 每天下午 6 點更新
    twse_api_timeout: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
