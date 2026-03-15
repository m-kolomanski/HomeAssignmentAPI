from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    FILE_STORAGE: Path = Path("./userfiles")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str):
        if field_name == "FILE_STORAGE":
            return Path(raw_val)
        return raw_val

settings = Settings()
