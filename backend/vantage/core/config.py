"""Vantage configuration settings."""
from __future__ import annotations

import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VANTAGE_",
        env_file=".env",
        extra="ignore",
    )

    environment: str = "development"
    debug: bool = True
    version: str = "0.1.0"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])

    # Local SQLite Database
    db_path: Path = Field(
        default_factory=lambda: Path(os.path.expanduser("~")) / ".vantage" / "vantage.db"
    )

    # External AI Providers (Optional - agents use fallback synthesizers if absent)
    groq_api_key: str = Field(default="")
    gemini_api_key: str = Field(default="")
    google_api_key: str = Field(default="")
    tavily_api_key: str = Field(default="")

    # Ingestion schedule & bounds
    ingest_interval_minutes: int = 60
    max_entities_per_adapter: int = 50

    log_level: str = "INFO"


def get_settings() -> Settings:
    return Settings()
