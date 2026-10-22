from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)
    app_name: str = "Industrial Quality Control System"
    app_env: Literal["development", "test", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    database_path: Path = Path("./data/inspection.sqlite3")
    artifacts_dir: Path = Path("./artifacts")
    log_level: str = "INFO"
    cameras_json: str = "[]"
    inference_backend: Literal["disabled", "yolo"] = "disabled"
    model_path: str | None = None
    model_version: str = "unconfigured"

@lru_cache
def get_settings() -> Settings:
    return Settings()
