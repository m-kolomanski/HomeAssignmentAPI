from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    FILE_STORAGE: Path = Field(alias = "FILE_STORAGE", default = Path("./userfiles"))
    DB_PATH: Path = Field(alias = "DB_PATH", default = Path("./app.db"))

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
    )

    @field_validator("FILE_STORAGE", mode = "after")
    @classmethod
    def validate_file_storage(cls, raw_val: str):
        path = Path(raw_val)
        path.mkdir(exist_ok = True)
        return path
    
    @field_validator("DB_PATH", mode = "after")
    @classmethod
    def validate_db_path(cls, raw_val: str):
        path = Path(raw_val)
        return path

settings = Settings()
