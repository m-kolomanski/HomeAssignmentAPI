from abc import ABC, abstractmethod
from polars import LazyFrame
from pathlib import Path
import logging

from backend.exceptions import FileNotFoundException

logger = logging.getLogger(__name__)


class FileStorage(ABC):
    def __init__(self, base_path: Path):
        self.base_path = base_path

    @property
    @abstractmethod
    def extension(self) -> str: ...

    def get_path(self, file_id: int) -> Path:
        return self.base_path / f"{file_id}.{self.extension}"

    def write(self, file_id: int, lf: LazyFrame, overwrite: bool = False) -> Path:
        file_path = self.get_path(file_id)

        if overwrite:
            if not file_path.exists():
                raise FileNotFoundException(f"File with ID {file_id} not found")

            logger.info(f"Removing stale file {file_path}")
            file_path.unlink()

        if file_path.exists():
            logger.critical(f"File path {file_path} already exists in storage.")
            raise RuntimeError(f"File path {file_path} already exists in storage.")

        self._sink(lf, file_path)
        return file_path

    @abstractmethod
    def _sink(self, lf: LazyFrame, file_path: Path) -> None: ...

    def read(self, file_id: int) -> LazyFrame:
        file_path = self.get_path(file_id)
        if not file_path.exists():
            raise FileNotFoundException(f"File with ID {file_id} not found")
        return self._scan(file_path)

    @abstractmethod
    def _scan(self, file_path: Path) -> LazyFrame: ...
