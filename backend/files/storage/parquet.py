import logging
from pathlib import Path
from polars import LazyFrame, scan_parquet


from backend.files.storage.base import FileStorage

logger = logging.getLogger(__name__)


class ParquetFileStorage(FileStorage):
    @property
    def extension(self) -> str:
        return "parquet"

    def sink(self, lf: LazyFrame, file_path: Path) -> None:
        lf.sink_parquet(file_path)

    def scan(self, file_path: Path) -> LazyFrame:
        return scan_parquet(file_path)
