from backend.files.storage.base import FileStorage
from backend.files.storage.csv import CsvFileStorage
from backend.files.storage.parquet import ParquetFileStorage

from backend.config import settings

__all__ = ["FileStorage", "get_file_storage"]

_STORAGES: dict[str, type[FileStorage]] = {
    "csv": CsvFileStorage,
    "parquet": ParquetFileStorage,
}


def get_file_storage() -> FileStorage:
    storage = _STORAGES[settings.FILE_STORAGE_FORMAT]
    return storage(settings.FILE_STORAGE)
