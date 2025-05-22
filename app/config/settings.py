from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "AI Tutor Chat System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API settings
    API_PREFIX: str = "/api"
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # C3 Service settings
    C3_API_URL: str = "http://localhost:8000"
    C3_API_KEY: Optional[str] = None
    
    # LLM settings
    LLM_PROVIDER: str = "openai"  # openai, anthropic, etc.
    LLM_MODEL: str = "gpt-4"  # gpt-4, claude-3-opus, etc.
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()