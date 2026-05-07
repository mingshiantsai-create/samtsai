from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./chip_analysis.db"

    # API
    api_title: str = "籌碼分析軟體 API"
    api_version: str = "0.1.0"
    debug: bool = True

    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:5173"]

    # Data scraping
    update_schedule_hour: int = 18  # 每天下午 6 點更新
    twse_api_timeout: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
