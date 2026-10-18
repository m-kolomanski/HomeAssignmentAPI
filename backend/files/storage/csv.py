from pathlib import Path
from polars import LazyFrame, scan_csv

from backend.files.storage.base import FileStorage


class CsvFileStorage(FileStorage):
    @property
    def extension(self) -> str:
        return "csv"

    def _sink(self, lf: LazyFrame, file_path: Path) -> None:
        lf.sink_csv(file_path)

    def _scan(self, file_path: Path) -> LazyFrame:
        return scan_csv(file_path)
