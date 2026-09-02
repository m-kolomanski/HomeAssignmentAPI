import logging
from pathlib import Path
from polars import LazyFrame, scan_csv
from fastapi import HTTPException, status


from backend.files.storage.base import FileStorage

logger = logging.getLogger(__name__)


class CsvFileStorage(FileStorage):
    @property
    def extension(self) -> str:
        return "csv"

    def write(self, file_id: int, lf: LazyFrame, overwrite: bool = False) -> Path:
        file_path = self.get_path(file_id)

        if overwrite and file_path.exists():
            logger.info(f"Removing stale file {file_path}")
            file_path.unlink()

        if file_path.exists():
            logger.critical(f"File path {file_path} already exists in storage.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error during file processing",
            )

        lf.sink_csv(file_path)
        return file_path

    def read(self, file_id: int) -> LazyFrame:
        file_path = self.get_path(file_id)
        return scan_csv(file_path)
