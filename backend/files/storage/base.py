from abc import ABC, abstractmethod
from polars import LazyFrame
from pathlib import Path


class FileStorage(ABC):
    def __init__(self, base_path: Path):
        self.base_path = base_path

    @property
    @abstractmethod
    def extension(self) -> str: ...

    def get_path(self, file_id: int) -> Path:
        return self.base_path / f"{file_id}.{self.extension}"

    @abstractmethod
    def write(self, file_id: int, lf: LazyFrame, overwrite: bool = False) -> Path: ...

    @abstractmethod
    def read(self, file_id: int) -> LazyFrame: ...
