import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GOOGLE_API_KEY: str
    TAVILY_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # WordPress Configuration
    WP_URL: Optional[str] = None
    WP_USERNAME: Optional[str] = None
    WP_APP_PASSWORD: Optional[str] = None

    # Database
    DATABASE_URL: str = "sqlite:///./storage/blog_agent.db"

    # Gemini Settings
    GEMINI_MODEL: str = "gemini-1.5-pro"  # Using 1.5-pro as requested

settings = Settings()
