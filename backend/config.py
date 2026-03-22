from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    FILE_STORAGE: Path = Field(alias = "FILE_STORAGE", default = Path("./userfiles"))

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
    )

    @field_validator("FILE_STORAGE", mode = "after")
    @classmethod
    def validate_file_storage(cls, raw_val: str):
        path = Path(raw_val)
        if not path.exists():
            path.mkdir()
        return path

settings = Settings()
