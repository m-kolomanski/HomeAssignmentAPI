from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    FILE_STORAGE: Path = Field(alias="FILE_STORAGE", default=Path("./userfiles"))
    DB_PATH: Path = Field(alias="DB_PATH", default=Path("./app.db"))
    HAAPI_LOG_LEVEL: str = Field(default="INFO")
    HAAPI_LOG_FILE_PATH: str = Field(default="log.jsonl")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @field_validator("FILE_STORAGE", mode="after")
    @classmethod
    def validate_file_storage(cls, raw_val: str):
        path = Path(raw_val)
        path.mkdir(exist_ok=True)
        return path

    @field_validator("DB_PATH", mode="after")
    @classmethod
    def validate_db_path(cls, raw_val: str):
        path = Path(raw_val)
        return path

    @field_validator("HAAPI_LOG_LEVEL", mode="after")
    @classmethod
    def validate_log_level(cls, raw_val: str):
        log_level = raw_val.upper()
        if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise ValueError(f"Invalid log level: `{raw_val}. Must be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`,")
        return log_level

settings = Settings()
